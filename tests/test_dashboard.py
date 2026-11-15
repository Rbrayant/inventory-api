def test_dashboard_and_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Inventory workspace" in response.data
    assert client.get("/static/dashboard.js").status_code == 200
    assert client.get("/static/dashboard.css").status_code == 200


def test_dashboard_does_not_expose_write_token(client):
    assert b"test-token" not in client.get("/").data
    assert client.post("/items", json={
        "name": "Cable", "sku": "GUI-1", "quantity": 3,
    }).status_code == 401
