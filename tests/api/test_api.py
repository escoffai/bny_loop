from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_gems():
    r = client.get("/v1/gems")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_byproduct_lookup_404():
    assert client.get("/v1/byproducts/does-not-exist").status_code == 404


def test_run_simulation_smoke():
    profile = client.get("/v1/byproducts").json()[0]
    r = client.post("/v1/simulations", json={"byproduct": profile, "objective": "max_yield"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ranked"]
    assert body["ranked"] == sorted(
        body["ranked"], key=lambda x: x["objective_value"], reverse=True
    )
