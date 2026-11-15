from tests.test_api import add


def test_low_stock_filter(client):
    for quantity in (0, 4, 5, 10):
        assert add(client, quantity).status_code == 201
    results = client.get("/items?low_stock=true").json
    assert [item["quantity"] for item in results] == [0, 4]
    assert len(client.get("/items?low_stock=false").json) == 4
    assert client.get("/items?low_stock=invalid").status_code == 400
