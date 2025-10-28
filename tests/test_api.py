import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Save and restore the in-memory activities around each test for isolation."""
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(orig))


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_and_duplicate():
    activity = "Soccer Team"
    email = "testuser@example.com"

    # Signup should succeed
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_unregister_and_not_found():
    activity = "Basketball Team"
    email = "temp@example.com"

    # Sign up first
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Now unregister
    r2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregister someone who isn't signed up -> 404
    r3 = client.delete(f"/activities/{activity}/signup", params={"email": "noone@example.com"})
    assert r3.status_code == 404
