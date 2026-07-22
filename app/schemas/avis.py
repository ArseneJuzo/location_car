from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AvisCreate(BaseModel):
    vehicule_id: int
    note: int = Field(ge=1, le=5)
    commentaire: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AvisRead(BaseModel):
    id: int
    utilisateur_id: int
    vehicule_id: int
    note: int
    commentaire: Optional[str] = None
    date_creation: datetime
