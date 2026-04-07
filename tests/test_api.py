from fastapi.testclient import TestClient

from main import app


def _login(client: TestClient) -> str:
    response = client.post("/api/v1/auth/token", data={"username": "admin@energy.local", "password": "changeme"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_and_market_endpoints() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        latest = client.get("/api/v1/market/latest")
        assert latest.status_code == 200
        payload = latest.json()
        assert payload["spot_price"] >= 10

        history = client.get("/api/v1/market/history")
        assert history.status_code == 200
        assert len(history.json()) >= 1


def test_trade_flow() -> None:
    with TestClient(app) as client:
        token = _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        trade = client.post(
            "/api/v1/trades",
            json={"energy_type": "wind", "quantity": 25.0, "price": 42.5},
            headers=headers,
        )
        assert trade.status_code == 201
        assert trade.json()["total"] == 1062.5

        my_trades = client.get("/api/v1/trades", headers=headers)
        assert my_trades.status_code == 200
        assert len(my_trades.json()) >= 1

        optimization = client.post("/api/v1/optimize?energy_type=solar&quantity=120")
        assert optimization.status_code == 200
        assert optimization.json()["routing_strategy"] == "merit_order_optimization"
