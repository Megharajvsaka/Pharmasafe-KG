import unittest
from ml_engine.inference.gnn_predictor import GNNPredictor, get_predictor


class TestGNN(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = get_predictor()

    def test_gnn_predict_known_pair(self):
        if not self.predictor.is_loaded:
            self.skipTest("GNN weights not present on this machine")
        prob = self.predictor.predict("warfarin", "aspirin")
        self.assertIsNotNone(prob)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_gnn_predict_oov(self):
        prob = self.predictor.predict("notadrug_xyz_123", "paracetamol")
        self.assertIsNone(prob)

    def test_gnn_predictor_singleton(self):
        p1 = get_predictor()
        p2 = get_predictor()
        self.assertIs(p1, p2)


if __name__ == "__main__":
    unittest.main()
