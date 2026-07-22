import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.middlewares.logging_middleware import LoggingMiddleware
from app.utils.storage import UPLOAD_DIR

tags_metadata = [
    {
        "name": "Auth",
        "description": "Inscription, connexion, rafraîchissement de token et réinitialisation de mot de passe.",
    },
    {
        "name": "Users",
        "description": "Gestion des comptes utilisateurs (clients, agences, administrateurs).",
    },
    {
        "name": "Agences",
        "description": "Agences de location présentes sur le territoire camerounais (Douala, Yaoundé, Bafoussam, ...).",
    },
    {
        "name": "Vehicules",
        "description": "Parc automobile proposé à la location par les agences.",
    },
    {
        "name": "Reservations",
        "description": "Réservations de véhicules par les clients et suivi de leur statut.",
    },
    {
        "name": "Paiements",
        "description": "Paiements associés à une réservation (montants exprimés en FCFA / XAF).",
    },
    {
        "name": "Avis",
        "description": "Avis et notes laissés par les clients sur les véhicules loués.",
    },
]

app = FastAPI(
    title="API Location Car Cameroun",
    description=(
        "API REST pour une plateforme de location de voitures opérant au Cameroun "
        "(Douala, Yaoundé, Bafoussam, Garoua, Bamenda, ...). "
        "Authentification par JWT (RS256), contrôle d'accès par rôle "
        "(client / agence / administrateur). Tous les montants sont exprimés en FCFA (XAF)."
    ),
    version="1.0.0",
    contact={
        "name": "Location Car Cameroun",
        "email": "arsenejuzo@gmail.com",
    },
    openapi_tags=tags_metadata,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"], summary="Vérifier que l'API est en ligne")
def root():
    return {"message": "API Location Car Cameroun en ligne", "docs": "/docs"}
