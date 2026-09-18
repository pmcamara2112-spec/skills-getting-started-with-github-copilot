from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "Basketball Team" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_rejects_duplicate_email():
    activity_name = "Chess Club"
    original_participants = list(activities[activity_name]["participants"])

    try:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": original_participants[0]},
        )

        assert response.status_code == 400
        assert "déjà inscrit" in response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants


def test_signup_rejects_full_activity():
    activity_name = "Art Club"
    original_participants = list(activities[activity_name]["participants"])
    original_max = activities[activity_name]["max_participants"]

    try:
        activities[activity_name]["participants"] = [f"student{i}@mergington.edu" for i in range(original_max)]
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "newstudent@mergington.edu"},
        )

        assert response.status_code == 400
        assert "complète" in response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["max_participants"] = original_max


def test_unregister_student_removes_participant():
    activity_name = "Basketball Team"
    original_participants = list(activities[activity_name]["participants"])

    try:
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": original_participants[0]},
        )

        assert response.status_code == 200
        assert original_participants[0] not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants
