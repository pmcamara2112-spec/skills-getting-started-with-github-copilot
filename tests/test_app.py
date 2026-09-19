import copy

import pytest
from src import app as app_module
from fastapi.testclient import TestClient

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_seed_data():
    # Arrange
    expected_activities = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activities.issubset(response.json())


def test_signup_rejects_duplicate_email():
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    app_module.activities[activity_name]["participants"] = [
        "existing.student@mergington.edu"
    ]

    # Act
    first = client.post(f"/activities/{activity_name}/signup?email={email}")
    second = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"].lower()


def test_signup_respects_capacity_limit():
    # Arrange
    activity_name = "Basketball Team"
    max_participants = app_module.activities[activity_name]["max_participants"]
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(max_participants)
    ]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "remove.me@mergington.edu"
    app_module.activities[activity_name]["participants"] = [
        "existing.student@mergington.edu"
    ]

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert email.lower() not in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_email_case_insensitive():
    # Arrange
    activity_name = "Chess Club"
    email = "  existing.student@mergington.edu  "
    app_module.activities[activity_name]["participants"] = [
        "existing.student@mergington.edu"
    ]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_requires_email_value():
    # Arrange
    activity_name = "Gym Class"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=")

    # Assert
    assert response.status_code == 400
    assert "email is required" in response.json()["detail"].lower()


def test_signup_rejects_unknown_activity():
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unknown_participant():
    # Arrange
    activity_name = "Drama Club"
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()
