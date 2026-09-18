"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


def normalize_email(email: str) -> str:
    return email.strip().lower()


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball training and games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Swimming Club": {
        "description": "Swimming training and water sports",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and visual design",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Acting, improvisation, and stage performance",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Math Club": {
        "description": "Problem-solving, contests, and advanced math activities",
        "schedule": "Fridays, 2:30 PM - 3:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Debate Team": {
        "description": "Research, public speaking, and argument practice",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str = Query(...)):
    """Sign up a student for an activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = normalize_email(email)

    if not normalized_email:
        raise HTTPException(status_code=400, detail="Email is required")

    if normalized_email in {normalize_email(participant) for participant in activity["participants"]}:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_for_activity(activity_name: str, email: str = Query(...)):
    """Unregister a student from an activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = normalize_email(email)

    if normalized_email not in {normalize_email(participant) for participant in activity["participants"]}:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    activity["participants"] = [
        participant for participant in activity["participants"]
        if normalize_email(participant) != normalized_email
    ]
    return {"message": f"Removed {normalized_email} from {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_for_activity_alias(activity_name: str, email: str = Query(...)):
    return unregister_for_activity(activity_name=activity_name, email=email)


@app.delete("/activities/{activity_name}/participants/{email}")
def unregister_for_activity_by_path(activity_name: str, email: str):
    return unregister_for_activity(activity_name=activity_name, email=email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
