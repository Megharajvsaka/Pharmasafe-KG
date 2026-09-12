import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.resolver_service import get_resolver


@pytest.fixture(scope="module")
def client():
    get_resolver().load()
    with TestClient(app) as c:
        yield c


class TestAPIClient:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "neo4j" in data
        assert "gnn_loaded" in data
        assert "brands_loaded" in data

    def test_search_endpoint(self, client):
        response = client.get("/search?q=Comb")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0

    def test_check_valid_combination(self, client):
        payload = {"drugs": ["Combiflam", "Ecosprin"]}
        response = client.post("/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_drugs"] == 2
        assert "interactions" in data
        assert "summary" in data

    def test_check_validation_too_few(self, client):
        payload = {"drugs": ["Combiflam"]}
        response = client.post("/check", json=payload)
        assert response.status_code == 422

    def test_check_unresolved_drugs(self, client):
        payload = {"drugs": ["FAKEDRUG_ABC_123", "ANOTHER_FAKEDRUG_XYZ"]}
        response = client.post("/check", json=payload)
        assert response.status_code == 422

    def test_drug_info_not_found(self, client):
        response = client.get("/drug/NONEXISTENT_BRAND_XYZ")
        assert response.status_code == 404
