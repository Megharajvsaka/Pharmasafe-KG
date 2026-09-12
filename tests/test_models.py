import unittest
from pydantic import ValidationError
from backend.app.domain.schemas.ddi import CheckRequest, InteractionResult, SafePair, ResolvedDrug


class TestModels(unittest.TestCase):
    def test_valid_check_request(self):
        req = CheckRequest(drugs=["Combiflam", "Ecosprin"])
        self.assertEqual(len(req.drugs), 2)

    def test_check_request_too_few_drugs(self):
        with self.assertRaises(ValidationError):
            CheckRequest(drugs=["Combiflam"])

    def test_check_request_too_many_drugs(self):
        with self.assertRaises(ValidationError):
            CheckRequest(drugs=[f"Drug_{i}" for i in range(11)])

    def test_check_request_whitespace_stripping(self):
        req = CheckRequest(drugs=["  Combiflam  ", " Ecosprin "])
        self.assertEqual(req.drugs, ["Combiflam", "Ecosprin"])

    def test_interaction_result_defaults(self):
        ir = InteractionResult(
            brand_a="DrugA",
            brand_b="DrugB",
            ingredient_a="GenericA",
            ingredient_b="GenericB",
            severity="MAJOR",
            mechanism="Test mechanism",
            explanation="Test explanation",
        )
        self.assertEqual(ir.status, "documented")
        self.assertEqual(ir.source, "knowledge_graph")
        self.assertIsNone(ir.confidence)
        self.assertEqual(ir.evidence, [])

    def test_predicted_interaction_result(self):
        ir = InteractionResult(
            brand_a="DrugA",
            brand_b="DrugB",
            ingredient_a="GenericA",
            ingredient_b="GenericB",
            severity="UNKNOWN",
            mechanism="AI Predicted link",
            status="predicted",
            source="gnn_predicted",
            confidence=0.885,
            evidence=[{"model": "GraphSAGE", "probability": 0.885}],
            explanation="AI prediction notice",
        )
        self.assertEqual(ir.status, "predicted")
        self.assertEqual(ir.source, "gnn_predicted")
        self.assertEqual(ir.confidence, 0.885)


if __name__ == "__main__":
    unittest.main()
