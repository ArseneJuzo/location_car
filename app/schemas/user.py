from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.utilisateur import RoleUtilisateur


class UserBase(BaseModel):
    nom_complet: str
    telephone: Optional[str] = None
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    mot_de_passe: str
    role: RoleUtilisateur = RoleUtilisateur.client


class UserUpdate(BaseModel):
    nom_complet: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    mot_de_passe: Optional[str] = None
    est_actif: Optional[bool] = None


class UserRead(UserBase):
    id: int
    role: RoleUtilisateur
    est_actif: bool
    date_creation: datetime
