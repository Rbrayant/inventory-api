import os

import pytest

from app.main import create_app


@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"),
                    reason="PostgreSQL integration URL not supplied")
def test_postgres_shared_storage(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "integration-token")
    first = create_app(os.environ["TEST_POSTGRES_URL"])
    second = create_app(os.environ["TEST_POSTGRES_URL"])
    metadata = first.extensions["metadata"]
    engine = first.extensions["database"]
    # This URL must refer to a disposable CI/test database.
    metadata.drop_all(engine)
    metadata.create_all(engine)
    auth = {"Authorization": "Bearer integration-token"}
    try:
        record = first.test_client().post(
            "/items", json={"name": "Shared", "sku": "Integration"},
            headers=auth,
        )
        assert record.status_code == 201
        assert second.test_client().get("/items").json[0]["id"] == (
            record.json["id"]
        )
        assert second.test_client().get("/ready").status_code == 200
    finally:
        metadata.drop_all(engine)
        engine.dispose()
        second.extensions["database"].dispose()
