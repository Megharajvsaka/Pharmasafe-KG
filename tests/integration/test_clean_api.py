def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["brands_loaded"] > 0

def test_check_endpoint(client):
    res = client.post("/check", json={"drugs": ["Combiflam", "Ecosprin"]})
    assert res.status_code == 200
    data = res.json()
    assert data["total_drugs"] == 2
    assert "interactions" in data
