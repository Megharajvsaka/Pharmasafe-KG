import pytest
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_token

def test_password_hash():
    pwd = "SecureDoctor@2026"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("Wrong", hashed) is False

def test_jwt_lifecycle():
    token = create_access_token(user_id="user-123", email="doc@test.org", role="clinician")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["email"] == "doc@test.org"
    assert payload["role"] == "clinician"
