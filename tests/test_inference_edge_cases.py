import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.resolver_service import get_resolver, ALIASES
from backend.app.infrastructure.neo4j_repository import Neo4jGraphRepository
from backend.app.services.ddi_service import DDIService
from ml_engine.inference.gnn_predictor import get_predictor


def check_interactions(generics_map):
    repo = Neo4jGraphRepository()
    pred = get_predictor()
    ddi = DDIService(repo, pred)
    return ddi.check_polypharmacy(generics_map)


class TestSynonymAndResolverEdgeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_resolver().load()

    def test_glibenclamide_glyburide_synonym(self):
        res = get_resolver().resolve_brand("glibenclamide")
        self.assertTrue("glibenclamide" in res["generics"] or "glyburide" in res["generics"])

    def test_paracetamol_acetaminophen_synonym(self):
        res = get_resolver().resolve_brand("paracetamol")
        self.assertTrue("paracetamol" in res["generics"] or "acetaminophen" in res["generics"])

    def test_aspirin_acetylsalicylic_acid_synonym(self):
        res = get_resolver().resolve_brand("aspirin")
        self.assertTrue("aspirin" in res["generics"] or "acetylsalicylic acid" in res["generics"])

    def test_amoxicillin_amoxycillin_synonym(self):
        res = get_resolver().resolve_brand("amoxicillin")
        self.assertTrue("amoxicillin" in res["generics"] or "amoxycillin" in res["generics"])


class TestGNNInferenceSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = get_predictor()

    def test_gnn_predictor_oov_returns_none(self):
        prob = self.predictor.predict("unknown_chemical_x", "unknown_chemical_y")
        self.assertIsNone(prob)

    def test_gnn_predicted_severity_is_unknown(self):
        generics_map = {
            "DrugA": ["paracetamol"],
            "DrugB": ["aspirin"],
        }
        res = check_interactions(generics_map)
        for inter in res["interactions"]:
            if inter.get("status") == "predicted":
                self.assertIn(inter["severity"], ["UNKNOWN", "UNASSESSED"])
                self.assertIn("GraphSAGE", inter["mechanism"])

    def test_not_documented_pairs_have_clinical_disclaimer(self):
        generics_map = {
            "NonInteractingBrand1": ["pantoprazole"],
            "NonInteractingBrand2": ["cetirizine"],
        }
        res = check_interactions(generics_map)
        for pair in res.get("safe_pairs_detail", []):
            self.assertEqual(pair["status"], "not_documented")
            self.assertIn("does not guarantee clinical safety", pair["note"].lower())


class TestAPIEdgeCasesAndPolypharmacy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        get_resolver().load()

    def test_unresolved_drugs_raise_422(self):
        response = self.client.post("/check", json={"drugs": ["TOTALLY_FAKE_1", "TOTALLY_FAKE_2"]})
        self.assertEqual(response.status_code, 422)

    def test_polypharmacy_three_drugs(self):
        response = self.client.post("/check", json={"drugs": ["Combiflam", "Ecosprin", "Warfarin"]})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_drugs"], 3)
        self.assertIn("interactions", data)
        self.assertIn("resolved_drugs", data)


if __name__ == "__main__":
    unittest.main()
