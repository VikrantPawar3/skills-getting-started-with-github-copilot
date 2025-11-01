from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity check: some known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "teststudent+signup@example.com"

    # Ensure not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    participants = data[activity]["participants"]
    if email in participants:
        # Clean up if a previous run left it
        client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")

    # Sign up
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(signup_url)
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify present
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # Signing up again should fail with 400
    resp = client.post(signup_url)
    assert resp.status_code == 400

    # Unregister
    del_url = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    resp = client.delete(del_url)
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]
