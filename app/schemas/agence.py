from pydantic import BaseModel, EmailStr
from typing import optional


class AgenceBase(BaseModel):
    nom: str
    ville: str
    pays: str
    telephone: int
    email: EmailStr

class AgenceCreate(AgenceBase):
    mot_de_passe: str

class AgenceUpdate(AgenceBase):
    mot_de_passe:optional[str] = none

class AgenceRead(AgenceBase):
    id: int

class config:
    orm_mode = True    