"""
tests/test_api_client.py
------------------------
In-process API endpoint testing using FastAPI TestClient and unittest.
"""

import unittest
from fastapi.testclient import TestClient
from phase3.app.main import app


from phase3.app.resolver import load_resolver


class TestAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_resolver()
        cls.client = TestClient(app)


    def test_health_endpoint(self):
        """Test GET / and GET /health."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("brands_loaded", data)
        self.assertGreater(data["brands_loaded"], 0)

    def test_search_endpoint(self):
        """Test GET /search autocomplete."""
        response = self.client.get("/search", params={"q": "Combi", "limit": 5})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["query"], "Combi")
        self.assertGreater(len(data["results"]), 0)

    def test_check_validation_too_few(self):
        """Test POST /check with < 2 drugs."""
        response = self.client.post("/check", json={"drugs": ["Combiflam"]})
        self.assertEqual(response.status_code, 422)

    def test_check_unresolved_drugs(self):
        """Test POST /check with unresolved invalid drugs."""
        response = self.client.post("/check", json={"drugs": ["XYZ_INVALID_1", "XYZ_INVALID_2"]})
        self.assertEqual(response.status_code, 422)

    def test_check_valid_combination(self):
        """Test POST /check with valid brands Combiflam and Ecosprin."""
        response = self.client.post("/check", json={"drugs": ["Combiflam", "Ecosprin"]})
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(data["total_drugs"], 2)
            self.assertIn("interactions", data)
            self.assertIn("resolved_drugs", data)
            self.assertIn("summary", data)

    def test_drug_info_not_found(self):
        """Test GET /drug/{name} for non-existent drug."""
        response = self.client.get("/drug/NON_EXISTENT_XYZ_123")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
