from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
DATA = Path(__file__).parent.parent / "sample_data"


def _post(name):
    with open(DATA / name, "rb") as f:
        return client.post("/validate", files={"file": (name, f, "text/csv")})


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_home_page_loads():
    r = client.get("/")
    assert r.status_code == 200
    assert "Data Quality Pipeline" in r.text


def test_clean_file_passes():
    body = _post("clean_dataset.csv").json()
    assert body["passed"] is True
    assert body["quality_score"] == 100.0


def test_corrupt_file_fails():
    body = _post("corrupt_dataset.csv").json()
    assert body["passed"] is False
    assert body["quality_score"] == 14.3
    assert {"duplicate", "missing_value", "invalid_type", "out_of_range",
            "invalid_value"} <= set(body["issues_by_check"])


def test_rejects_non_csv():
    r = client.post("/validate", files={"file": ("x.txt", b"hi", "text/plain")})
    assert r.status_code == 400
