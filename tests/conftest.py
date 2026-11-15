import pytest

from app.main import create_app


@pytest.fixture
def application(tmp_path, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "test-token")
    monkeypatch.setenv("APP_VERSION", "test-version")
    app = create_app(f"sqlite:///{tmp_path / 'test.db'}")
    app.config["TESTING"] = True
    app.extensions["metadata"].create_all(app.extensions["database"])
    yield app
    app.extensions["database"].dispose()


@pytest.fixture
def client(application):
    return application.test_client()
