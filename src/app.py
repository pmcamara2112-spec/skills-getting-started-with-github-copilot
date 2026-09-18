"""
API de gestion du lycée

Une application FastAPI très simple qui permet aux élèves de consulter
les activités extrascolaires du lycée Mergington et de s'y inscrire.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="API du lycée Mergington",
    description="API permettant de consulter les activités extrascolaires et de s'y inscrire",
)

# Monter le répertoire contenant les fichiers statiques
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)


def normalize_email(email: str) -> str:
    return email.strip().lower()


# Base de données des activités en mémoire
activities = {
    "Chess Club": {
        "description": "Apprendre des stratégies et participer à des tournois d'échecs",
        "schedule": "Vendredi, de 15 h 30 à 17 h 00",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Apprendre les bases de la programmation et créer des projets logiciels",
        "schedule": "Mardi et jeudi, de 15 h 30 à 16 h 30",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Éducation physique et activités sportives",
        "schedule": "Lundi, mercredi et vendredi, de 14 h 00 à 15 h 00",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Entraînement et matchs de basketball en compétition",
        "schedule": "Mardi et jeudi, de 16 h 00 à 18 h 00",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"],
    },
    "Swimming Club": {
        "description": "Entraînement de natation et sports nautiques",
        "schedule": "Lundi et mercredi, de 15 h 30 à 17 h 00",
        "max_participants": 20,
        "participants": [],
    },
    "Art Club": {
        "description": "Découvrir la peinture, le dessin et les arts visuels",
        "schedule": "Mercredi, de 15 h 30 à 17 h 00",
        "max_participants": 15,
        "participants": ["ava@mergington.edu"],
    },
    "Drama Club": {
        "description": "Pratiquer le théâtre, l'improvisation et la scène",
        "schedule": "Mardi, de 16 h 00 à 18 h 00",
        "max_participants": 18,
        "participants": [],
    },
    "Math Olympiad": {
        "description": "Résoudre des problèmes de mathématiques avancés et participer à des concours",
        "schedule": "Jeudi, de 15 h 30 à 17 h 00",
        "max_participants": 16,
        "participants": ["noah@mergington.edu"],
    },
    "Science Club": {
        "description": "Réaliser des expériences et explorer les sciences",
        "schedule": "Vendredi, de 15 h 30 à 17 h 00",
        "max_participants": 20,
        "participants": [],
    },
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Inscrire un élève à une activité."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activité introuvable")

    activity = activities[activity_name]
    normalized_email = normalize_email(email)

    if not normalized_email:
        raise HTTPException(status_code=400, detail="L'adresse e-mail est obligatoire")

    participants = [normalize_email(participant) for participant in activity.get("participants", [])]
    if normalized_email in participants:
        raise HTTPException(
            status_code=400,
            detail="L'élève est déjà inscrit à cette activité",
        )

    max_participants = int(activity.get("max_participants", 0))
    if len(participants) >= max_participants:
        raise HTTPException(status_code=400, detail="L'activité est complète")

    participants.append(normalized_email)
    activity["participants"] = participants
    return {"message": f"{normalized_email} est inscrit à l'activité {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_student(activity_name: str, email: str):
    """Désinscrire un élève d'une activité."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activité introuvable")

    activity = activities[activity_name]
    normalized_email = normalize_email(email)
    participants = [normalize_email(participant) for participant in activity.get("participants", [])]

    if normalized_email not in participants:
        raise HTTPException(
            status_code=404,
            detail="L'élève n'est pas inscrit à cette activité",
        )

    activity["participants"] = [participant for participant in participants if participant != normalized_email]
    return {
        "message": f"{normalized_email} a été désinscrit de l'activité {activity_name}"
    }
