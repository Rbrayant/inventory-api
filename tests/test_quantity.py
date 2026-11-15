import pytest

from tests.test_api import AUTH, add


@pytest.mark.parametrize("quantity", [-1, True, "90", None, 2.5, 2147483648])
def test_invalid_quantity(client, quantity):
    item = add(client).json
    response = client.patch(f"/items/{item['id']}",
                            json={"quantity": quantity}, headers=AUTH)
    assert response.status_code == 400
    assert client.get("/items").json[0]["quantity"] == 10


@pytest.mark.parametrize("quantity", [-1, True, "90", None, 2.5, 2147483648])
def test_create_invalid_quantity(client, quantity):
    response = client.post("/items", headers=AUTH, json={
        "name": "Mouse", "sku": "MOUSE-1", "quantity": quantity,
    })
    assert response.status_code == 400
    assert client.get("/items").json == []


@pytest.mark.parametrize("quantity", [0, 100, 2147483647])
def test_quantity_boundaries(client, quantity):
    item = add(client).json
    response = client.patch(f"/items/{item['id']}",
                            json={"quantity": quantity}, headers=AUTH)
    assert response.status_code == 200
    assert response.json["quantity"] == quantity
