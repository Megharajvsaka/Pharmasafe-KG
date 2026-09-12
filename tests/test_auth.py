import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal, init_db
from backend.app.domain.models.user import User, RefreshToken, SavedRegimen, AnalysisHistory
from backend.app.core.security import hash_password, verify_password


@pytest.fixture(autouse=True)
def clean_database():
    init_db()
    db = SessionLocal()
    try:
        db.query(RefreshToken).delete()
        db.query(SavedRegimen).delete()
        db.query(AnalysisHistory).delete()
        db.query(User).filter(User.email.like("%@test-pharma.org")).delete()
        db.commit()
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        db.query(RefreshToken).delete()
        db.query(SavedRegimen).delete()
        db.query(AnalysisHistory).delete()
        db.query(User).filter(User.email.like("%@test-pharma.org")).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pwd = "ClinicalSecret@2026"
        hashed = hash_password(pwd)
        assert hashed != pwd
        assert hashed.startswith("$argon2id$")
        assert verify_password(pwd, hashed) is True
        assert verify_password("WrongPassword@123", hashed) is False

    def test_short_password_rejected(self):
        with pytest.raises(ValueError):
            hash_password("short1")


class TestUserRegistrationAndLogin:
    def test_registration_success(self, client):
        payload = {
            "email": "Dr.Sharma@test-pharma.org",
            "password": "SecurePassword@123",
            "full_name": "Dr. Ananya Sharma",
            "role": "clinician",
            "institution": "AIIMS New Delhi",
        }
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "dr.sharma@test-pharma.org"
        assert data["user"]["full_name"] == "Dr. Ananya Sharma"
        assert data["user"]["role"] == "clinician"
        assert data["user"]["is_active"] is True
        assert "password_hash" not in data["user"]
        assert "pharmasafe_refresh_token" in res.cookies

    def test_duplicate_registration_fails(self, client):
        payload = {
            "email": "dr.sharma@test-pharma.org",
            "password": "AnotherPassword@999",
            "full_name": "Duplicate User",
            "role": "researcher",
        }
        client.post("/auth/register", json=payload)
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 409
        assert "already registered" in res.json()["detail"]

    def test_invalid_email_registration_fails(self, client):
        payload = {
            "email": "not-an-email",
            "password": "SecurePassword@123",
            "full_name": "Invalid Email",
        }
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 422

    def test_login_success(self, client):
        client.post(
            "/auth/register",
            json={
                "email": "dr.sharma@test-pharma.org",
                "password": "SecurePassword@123",
                "full_name": "Dr. Ananya Sharma",
                "role": "clinician",
            }
        )
        payload = {
            "email": "dr.sharma@test-pharma.org",
            "password": "SecurePassword@123",
        }
        res = client.post("/auth/login", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "dr.sharma@test-pharma.org"

    def test_login_wrong_password(self, client):
        client.post(
            "/auth/register",
            json={
                "email": "dr.sharma@test-pharma.org",
                "password": "SecurePassword@123",
                "full_name": "Dr. Ananya Sharma",
                "role": "clinician",
            }
        )
        payload = {
            "email": "dr.sharma@test-pharma.org",
            "password": "IncorrectPassword@123",
        }
        res = client.post("/auth/login", json=payload)
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        payload = {
            "email": "nonexistent@test-pharma.org",
            "password": "SomePassword@123",
        }
        res = client.post("/auth/login", json=payload)
        assert res.status_code == 401

    def test_get_me_authenticated(self, client):
        reg_res = client.post(
            "/auth/register",
            json={
                "email": "dr.sharma@test-pharma.org",
                "password": "SecurePassword@123",
                "full_name": "Dr. Ananya Sharma",
                "role": "clinician",
                "institution": "AIIMS New Delhi",
            }
        )
        token = reg_res.json()["access_token"]
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "dr.sharma@test-pharma.org"
        assert data["role"] == "clinician"
        assert data["institution"] == "AIIMS New Delhi"

    def test_get_me_unauthorized_without_token(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 401

    def test_refresh_token_rotation(self, client):
        reg_res = client.post(
            "/auth/register",
            json={
                "email": "dr.sharma@test-pharma.org",
                "password": "SecurePassword@123",
                "full_name": "Dr. Ananya Sharma",
                "role": "clinician",
            }
        )
        refresh_token = reg_res.cookies.get("pharmasafe_refresh_token")
        assert refresh_token is not None

        ref_res = client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert ref_res.status_code == 200
        data = ref_res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "dr.sharma@test-pharma.org"

    def test_logout(self, client):
        reg_res = client.post(
            "/auth/register",
            json={
                "email": "dr.sharma@test-pharma.org",
                "password": "SecurePassword@123",
                "full_name": "Dr. Ananya Sharma",
                "role": "clinician",
            }
        )
        refresh_token = reg_res.cookies.get("pharmasafe_refresh_token")
        logout_res = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "ok"


class TestSavedRegimensAndHistoryTenantIsolation:
    def test_regimen_crud_and_isolation(self, client):
        res_a = client.post(
            "/auth/register",
            json={
                "email": "doctor_a@test-pharma.org",
                "password": "PasswordA@123",
                "full_name": "Doctor A",
                "role": "clinician",
            },
        )
        token_a = res_a.json()["access_token"]

        res_b = client.post(
            "/auth/register",
            json={
                "email": "doctor_b@test-pharma.org",
                "password": "PasswordB@123",
                "full_name": "Doctor B",
                "role": "researcher",
            },
        )
        token_b = res_b.json()["access_token"]

        create_res = client.post(
            "/users/me/regimens",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "name": "Cardiology Triple Therapy",
                "drugs": ["Atorva 10", "Ecosprin", "Metolar XR"],
            },
        )
        assert create_res.status_code == 201
        regimen_a = create_res.json()

        list_a = client.get("/users/me/regimens", headers={"Authorization": f"Bearer {token_a}"})
        assert list_a.status_code == 200
        assert len(list_a.json()) >= 1
        assert list_a.json()[0]["id"] == regimen_a["id"]

        list_b = client.get("/users/me/regimens", headers={"Authorization": f"Bearer {token_b}"})
        assert list_b.status_code == 200
        assert len(list_b.json()) == 0

        del_b = client.delete(f"/users/me/regimens/{regimen_a['id']}", headers={"Authorization": f"Bearer {token_b}"})
        assert del_b.status_code == 404

        del_a = client.delete(f"/users/me/regimens/{regimen_a['id']}", headers={"Authorization": f"Bearer {token_a}"})
        assert del_a.status_code == 200

    def test_analysis_history_persistence_and_isolation(self, client):
        res_a = client.post(
            "/auth/register",
            json={
                "email": "doctor_a@test-pharma.org",
                "password": "PasswordA@123",
                "full_name": "Doctor A",
                "role": "clinician",
            },
        )
        token_a = res_a.json()["access_token"]

        res_b = client.post(
            "/auth/register",
            json={
                "email": "doctor_b@test-pharma.org",
                "password": "PasswordB@123",
                "full_name": "Doctor B",
                "role": "researcher",
            },
        )
        token_b = res_b.json()["access_token"]

        hist_create = client.post(
            "/users/me/history",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "drugs": ["Combiflam", "Warfarin"],
                "result_summary": {"major": 1, "moderate": 0, "minor": 0, "total": 1},
            },
        )
        assert hist_create.status_code == 201
        data = hist_create.json()
        assert data["drugs"] == ["Combiflam", "Warfarin"]

        hist_a = client.get("/users/me/history", headers={"Authorization": f"Bearer {token_a}"})
        assert hist_a.status_code == 200
        assert len(hist_a.json()) >= 1

        hist_b = client.get("/users/me/history", headers={"Authorization": f"Bearer {token_b}"})
        assert hist_b.status_code == 200
        assert len(hist_b.json()) == 0
