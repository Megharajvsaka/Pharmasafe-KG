"""
tests/test_models.py
--------------------
Unit tests for FastAPI Pydantic request and response models using unittest.
"""

import unittest
from pydantic import ValidationError
from phase3.app.models import CheckRequest, InteractionResult, SafePair, ResolvedDrug


class TestModels(unittest.TestCase):
    def test_valid_check_request(self):
        """Test valid CheckRequest with 2 to 10 drugs."""
        req = CheckRequest(drugs=["Combiflam", "Ecosprin"])
        self.assertEqual(req.drugs, ["Combiflam", "Ecosprin"])

    def test_check_request_whitespace_stripping(self):
        """Test that whitespace in drug names is stripped."""
        req = CheckRequest(drugs=["  Combiflam  ", " Ecosprin "])
        self.assertEqual(req.drugs, ["Combiflam", "Ecosprin"])

    def test_check_request_too_few_drugs(self):
        """Test that <2 drugs raises ValidationError."""
        with self.assertRaises(ValidationError):
            CheckRequest(drugs=["Combiflam"])

    def test_check_request_too_many_drugs(self):
        """Test that >10 drugs raises ValidationError."""
        with self.assertRaises(ValidationError):
            CheckRequest(drugs=[f"Drug_{i}" for i in range(12)])

    def test_interaction_result_defaults(self):
        """Test InteractionResult default status and source."""
        res = InteractionResult(
            brand_a="Combiflam",
            brand_b="Ecosprin",
            ingredient_a="ibuprofen",
            ingredient_b="aspirin",
            severity="MAJOR",
            mechanism="Increased bleeding risk",
            explanation="Major interaction detected",
        )
        self.assertEqual(res.status, "documented")
        self.assertEqual(res.source, "knowledge_graph")
        self.assertIsNone(res.confidence)
        self.assertEqual(res.evidence, [])

    def test_predicted_interaction_result(self):
        """Test InteractionResult for AI predicted status."""
        res = InteractionResult(
            brand_a="Drug A",
            brand_b="Drug B",
            ingredient_a="ing_a",
            ingredient_b="ing_b",
            severity="MODERATE",
            mechanism="Predicted link",
            explanation="AI predicted interaction",
            status="predicted",
            source="gnn_predicted",
            confidence=0.854,
        )
        self.assertEqual(res.status, "predicted")
        self.assertEqual(res.source, "gnn_predicted")
        self.assertEqual(res.confidence, 0.854)


if __name__ == "__main__":
    unittest.main()
