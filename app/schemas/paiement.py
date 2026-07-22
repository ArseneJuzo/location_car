from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PaiementCreate(BaseModel):
    reservation_id: int
    montant: float
    methode: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaiementUpdateStatut(BaseModel):
    statut: str


class PaiementRead(BaseModel):
    id: int
    reservation_id: int
    montant: float
    statut: str
    methode: Optional[str] = None
    date_paiement: datetime
