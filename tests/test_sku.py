from tests.test_api import AUTH


def test_duplicate_sku_rejected(client):
    data = {"name": "Keyboard", "sku": "KB-1", "quantity": 5}
    assert client.post("/items", json=data, headers=AUTH).status_code == 201
    assert client.post("/items", json=data, headers=AUTH).status_code == 409
    assert len(client.get("/items").json) == 1
