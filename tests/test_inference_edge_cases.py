"""
test_inference_edge_cases.py
-----------------------------
Comprehensive tests for runtime inference edge-cases, canonical synonym resolution,
GNN fallback semantics, severity preservation, and polypharmacy handling.
"""

import pytest
from fastapi.testclient import TestClient
from phase3.app.main import app
from phase3.app.resolver import resolve_brand, ALIASES
from phase3.app.query_engine import check_interactions
from phase4.gnn_inference import get_predictor


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestSynonymAndResolverEdgeCases:
    """Tests for canonical identity / synonym resolution."""

    def test_glibenclamide_glyburide_synonym(self):
        result = resolve_brand("glibenclamide")
        assert result["match_type"] == "alias"
        assert "glyburide" in result["generics"]
        assert "glibenclamide" in result["generics"]

    def test_paracetamol_acetaminophen_synonym(self):
        result = resolve_brand("paracetamol")
        assert "paracetamol" in result["generics"]
        assert "acetaminophen" in result["generics"]

    def test_aspirin_acetylsalicylic_acid_synonym(self):
        result = resolve_brand("aspirin")
        assert "aspirin" in result["generics"]
        assert "acetylsalicylic acid" in result["generics"]

    def test_amoxicillin_amoxycillin_synonym(self):
        result = resolve_brand("amoxycillin")
        assert result["match_type"] == "alias"
        assert "amoxicillin" in result["generics"]


class TestGNNInferenceSemantics:
    """Tests GNN prediction semantics, severity unassessed tag, and OOV safety."""

    def test_gnn_predictor_oov_returns_none(self):
        predictor = get_predictor()
        assert predictor.is_loaded is True
        prob = predictor.predict("completely_unknown_molecule_xyz", "aspirin")
        assert prob is None

    def test_gnn_predicted_severity_is_unknown(self):
        """Simulate a GNN prediction fallback to ensure severity is explicitly UNKNOWN."""
        generics_map = {
            "DrugA": ["paracetamol"],
            "DrugB": ["aspirin"],
        }
        res = check_interactions(generics_map)
        assert res["total_drugs"] == 2
        for inter in res["interactions"]:
            if inter.get("status") == "predicted":
                assert inter["severity"] == "UNKNOWN"
                assert inter["source"] == "gnn_predicted"
                assert inter["confidence"] is not None
                assert inter["confidence"] >= 0.70

    def test_not_documented_pairs_have_clinical_disclaimer(self):
        """Pairs with no interaction evidence must NOT be blindly called 'safe'."""
        generics_map = {
            "NonInteractingBrand1": ["pantoprazole"],
            "NonInteractingBrand2": ["cetirizine"],
        }
        res = check_interactions(generics_map)
        for safe in res["safe_pairs_detail"]:
            assert "not guaranteed" in safe["note"].lower() or "not documented" in safe["note"].lower()
            assert safe["status"] == "not_documented"


class TestAPIEdgeCasesAndPolypharmacy:
    """Tests end-to-end API edge-cases."""

    def test_unresolved_drugs_raise_422(self, client):
        resp = client.post("/check", json={"drugs": ["fake_xyz_12345", "fake_abc_67890"]})
        assert resp.status_code == 422
        assert "Could not resolve enough drug names" in resp.json()["detail"]

    def test_polypharmacy_three_drugs(self, client):
        resp = client.post("/check", json={"drugs": ["Combiflam", "Ecosprin", "Dolo 650"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_drugs"] == 3
        assert "interactions" in data
        assert "safe_pairs_detail" in data
        assert "resolved_drugs" in data
        assert len(data["resolved_drugs"]) == 3
