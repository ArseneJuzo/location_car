from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional

class UserBase(BaseModel):
    nom_complet: str
    telephone: str
    email: EmailStr
    est_actif: Optional[bool] = True

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    mot_de_passe: str

class UserUpdate(UserBase):
    mot_de_passe: Optional[str] = None

class UserRead(UserBase):
    id: int
    
    