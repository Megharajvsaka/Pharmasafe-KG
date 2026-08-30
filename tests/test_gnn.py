"""
tests/test_gnn.py
-----------------
Unit tests for the GNNPredictor inference module using unittest.
"""

import unittest
from phase4.gnn_inference import GNNPredictor, get_predictor


class TestGNN(unittest.TestCase):
    def test_gnn_predictor_singleton(self):
        """Test get_predictor returns an initialized singleton instance."""
        predictor = get_predictor()
        self.assertIsNotNone(predictor)

    def test_gnn_predict_known_pair(self):
        """Test GNN prediction for known vocabulary drugs."""
        predictor = get_predictor()
        if predictor.is_loaded:
            prob = predictor.predict("warfarin", "aspirin")
            self.assertIsNotNone(prob)
            self.assertTrue(0.0 <= prob <= 1.0)

    def test_gnn_predict_oov(self):
        """Test GNN prediction returns None for out-of-vocabulary terms."""
        predictor = get_predictor()
        if predictor.is_loaded:
            prob = predictor.predict("non_existent_drug_123", "aspirin")
            self.assertIsNone(prob)


if __name__ == "__main__":
    unittest.main()
