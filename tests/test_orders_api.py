def test_orders_endpoint_returns_existing_orders(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 8
    assert payload[0]["order_id"] == "FE-48291"


def test_order_detail_returns_404_for_unknown_order(client):
    response = client.get("/api/orders/FE-DOES-NOT-EXIST")
    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}


def test_existing_api_does_not_expose_risk_score_field(client):
    response = client.get("/api/orders/FE-48291")
    assert response.status_code == 200
    payload = response.get_json()
    assert "risk_score" not in payload
    assert "estimated_delay_minutes" in payload


def test_at_risk_endpoint_applies_rule_and_sorts_by_delay(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == sorted(delays, reverse=True)
    assert all(order["status"] == "ACTIVE" and delay >= 10 for order, delay in zip(payload, delays))
    assert 10 in delays
    assert 9 not in delays
    assert all(delay is not None for delay in delays)
    assert all(order["status"] not in {"DELIVERED", "CANCELLED"} for order in payload)


def test_at_risk_endpoint_does_not_change_existing_orders_contract(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.get_json()) == 8
