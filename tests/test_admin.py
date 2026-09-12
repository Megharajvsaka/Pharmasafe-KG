import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal, init_db
from backend.app.domain.models.user import User, RefreshToken, SavedRegimen, AnalysisHistory
from backend.app.core.security import hash_password, create_access_token


@pytest.fixture(autouse=True)
def clean_database():
    init_db()
    db = SessionLocal()
    try:
        db.query(RefreshToken).delete()
        db.query(SavedRegimen).delete()
        db.query(AnalysisHistory).delete()
        db.query(User).filter(User.email.like("%@admin-test.org")).delete()
        db.commit()
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        db.query(RefreshToken).delete()
        db.query(SavedRegimen).delete()
        db.query(AnalysisHistory).delete()
        db.query(User).filter(User.email.like("%@admin-test.org")).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestAdminRBACSecurity:
    def test_unauthorized_access_rejected(self, client):
        resp = client.get("/admin/users")
        assert resp.status_code == 401
        
        resp_stats = client.get("/admin/stats")
        assert resp_stats.status_code == 401

    def test_non_admin_role_forbidden(self, client):
        db = SessionLocal()
        student = User(
            email="student@admin-test.org",
            password_hash=hash_password("StudentSecure@2026"),
            full_name="Test Student",
            role="student",
            institution="Medical College"
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        db.close()

        token = create_access_token(user_id=student.id, email=student.email, role=student.role)
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/admin/users", headers=headers)
        assert resp.status_code == 403
        assert "Administrative privileges required" in resp.json()["detail"]

        resp_stats = client.get("/admin/stats", headers=headers)
        assert resp_stats.status_code == 403

    def test_admin_access_allowed(self, client):
        db = SessionLocal()
        admin = User(
            email="superadmin@admin-test.org",
            password_hash=hash_password("AdminSecure@2026"),
            full_name="Lead Administrator",
            role="admin",
            institution="PharmaSafe HQ"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        db.close()

        token = create_access_token(user_id=admin.id, email=admin.email, role=admin.role)
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/admin/users", headers=headers)
        assert resp.status_code == 200
        users = resp.json()
        assert isinstance(users, list)
        assert len(users) >= 1
        assert any(u["email"] == "superadmin@admin-test.org" for u in users)

        resp_stats = client.get("/admin/stats", headers=headers)
        assert resp_stats.status_code == 200
        stats = resp_stats.json()
        assert "total_users" in stats
        assert "users_by_role" in stats
        assert "total_brands_mapped" in stats
        assert stats["total_graph_nodes"] == 50073
