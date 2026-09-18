from src import app as app_module
from fastapi.testclient import TestClient

client = TestClient(app_module.app)


def reset_activity(activity_name, participants=None):
    app_module.activities[activity_name]["participants"] = list(participants or [])


def test_get_activities_returns_seed_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_rejects_duplicate_email():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    reset_activity(activity_name, ["existing.student@mergington.edu"])

    first = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first.status_code == 200

    second = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"].lower()


def test_signup_respects_capacity_limit():
    activity_name = "Basketball Team"
    max_participants = app_module.activities[activity_name]["max_participants"]
    reset_activity(activity_name, [f"student{i}@mergington.edu" for i in range(max_participants)])

    response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_unregister_removes_participant():
    activity_name = "Programming Class"
    email = "remove.me@mergington.edu"
    reset_activity(activity_name, ["existing.student@mergington.edu"])

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert delete_response.status_code == 200
    assert email.lower() not in client.get("/activities").json()[activity_name]["participants"]
