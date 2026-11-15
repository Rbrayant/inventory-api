from uuid import uuid4

import pytest

from app.main import create_app

AUTH = {"Authorization": "Bearer test-token"}


def add(client, quantity=10):
    return client.post("/items", json={
        "name": "USB Cable", "sku": "USB-" + uuid4().hex,
        "quantity": quantity,
    }, headers=AUTH)


def test_health_version_and_readiness(client):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/version").json["version"] == "test-version"


def test_create_list_update_delete(client):
    response = add(client)
    assert response.status_code == 201
    ident = response.json["id"]
    assert client.get("/items").json[0]["name"] == "USB Cable"
    response = client.patch(f"/items/{ident}", json={"quantity": 7},
                            headers=AUTH)
    assert response.status_code == 200
    assert response.json["quantity"] == 7
    assert client.delete(f"/items/{ident}", headers=AUTH).status_code == 204
    assert client.get("/items").json == []


@pytest.mark.parametrize("method,path,data", [
    ("post", "/items", {"name": "A", "sku": "B"}),
    ("patch", "/items/1", {"quantity": 80}),
    ("delete", "/items/1", None),
])
def test_write_requires_auth(client, method, path, data):
    assert getattr(client, method)(path, json=data).status_code == 401


@pytest.mark.parametrize("data", [
    [], {}, {"name": 1, "sku": "B"}, {"name": " ", "sku": "B"},
])
def test_invalid_item(client, data):
    assert client.post("/items", json=data, headers=AUTH).status_code == 400


def test_missing_item(client):
    response = client.patch("/items/999", json={"quantity": 70}, headers=AUTH)
    assert response.status_code == 404
    assert client.delete("/items/999", headers=AUTH).status_code == 404


def test_storage_shared_between_app_instances(application):
    first = application.test_client()
    add(first)
    engine = application.extensions["database"]
    second_app = create_app(str(engine.url))
    response = second_app.test_client().get("/items")
    assert response.json[0]["name"] == "USB Cable"
    second_app.extensions["database"].dispose()


def test_readiness_fails_without_schema(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'empty.db'}")
    assert app.test_client().get("/health").status_code == 200
    assert app.test_client().get("/ready").status_code == 503
    app.extensions["database"].dispose()
