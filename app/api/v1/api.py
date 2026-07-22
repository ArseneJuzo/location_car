from fastapi import APIRouter
from app.api.v1.endpoints import user, auth, agence, vehicule, reservation, paiement, avis

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(agence.router)
api_router.include_router(vehicule.router)
api_router.include_router(reservation.router)
api_router.include_router(paiement.router)
api_router.include_router(avis.router)
