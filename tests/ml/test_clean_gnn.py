from ml_engine.inference.gnn_predictor import get_predictor

def test_gnn_singleton():
    p = get_predictor()
    assert p is not None
    if p.is_loaded:
        score = p.predict("warfarin", "ibuprofen")
        assert score is None or 0.0 <= score <= 1.0
