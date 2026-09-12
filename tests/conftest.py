"""
conftest.py
-----------
Global pytest fixtures for PharmaSafe-KG.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal, init_db
from backend.app.domain.models.user import User, RefreshToken, SavedRegimen, AnalysisHistory


@pytest.fixture(autouse=True)
def clean_database():
    """Ensure database schema is created and test user records are cleaned up."""
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
