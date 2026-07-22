from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.vehicule import StatutVehicule, CategorieLocation


class VehiculeBase(BaseModel):
    marque: str
    modele: str
    immatriculation: str
    prix_journalier: float
    carburant: Optional[str] = None
    categorie: Optional[CategorieLocation] = None
    nombres_places: Optional[int] = None
    boite_vitesse: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VehiculeCreate(VehiculeBase):
    agence_id: Optional[int] = None


class VehiculeUpdate(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    immatriculation: Optional[str] = None
    prix_journalier: Optional[float] = None
    carburant: Optional[str] = None
    categorie: Optional[CategorieLocation] = None
    nombres_places: Optional[int] = None
    boite_vitesse: Optional[str] = None
    statut: Optional[StatutVehicule] = None
    image_url: Optional[str] = None


class VehiculeRead(VehiculeBase):
    id: int
    statut: StatutVehicule
    agence_id: Optional[int] = None
