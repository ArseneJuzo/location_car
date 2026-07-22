from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class AgenceBase(BaseModel):
    nom_agence: str
    adresse: str
    ville: Optional[str] = None
    pays: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class AgenceCreate(AgenceBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    responsable_id: Optional[int] = None


class AgenceUpdate(BaseModel):
    nom_agence: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AgenceRead(AgenceBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[float] = None
    total_avis: Optional[int] = None
    nombre_vehicule_disponibles: int
    nombre_vehicule_total: int
    nombre_reservation: int
    responsable_id: Optional[int] = None
    date_creation: datetime
    distance_km: Optional[float] = None
