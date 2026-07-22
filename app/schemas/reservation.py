from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.reservation import StatutReservation


class ReservationBase(BaseModel):
    vehicule_id: int
    date_debut: date
    date_fin: date

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdateStatut(BaseModel):
    statut: StatutReservation


class ReservationRead(ReservationBase):
    id: int
    utilisateur_id: int
    montant_total: float
    statut: StatutReservation
