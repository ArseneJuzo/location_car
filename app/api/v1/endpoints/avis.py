from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import avis_crud
from app.schemas.avis import AvisRead, AvisCreate
from app.core.dependencies import get_db
from app.middlewares.auth_middleware import require_role, get_current_user
from app.models.utilisateur import Utilisateur, RoleUtilisateur

router = APIRouter(prefix="/avis", tags=["Avis"])


@router.post(
    "/",
    response_model=AvisRead,
    status_code=status.HTTP_201_CREATED,
    summary="Laisser un avis (note 1-5) sur un véhicule (rôle client)",
)
def create_avis(
    avis: AvisCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.client)),
):
    return avis_crud.create_avis(db, avis, current_user.id)


@router.get("/vehicule/{vehicule_id}", response_model=List[AvisRead], summary="Lister les avis d'un véhicule (public)")
def list_avis_for_vehicule(vehicule_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return avis_crud.get_avis_by_vehicule(db, vehicule_id, skip, limit)


@router.delete("/{avis_id}", status_code=status.HTTP_200_OK, summary="Supprimer un avis (auteur ou administrateur)")
def delete_avis(
    avis_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    db_avis = avis_crud.get_avis(db, avis_id)
    if current_user.role != RoleUtilisateur.administrateur and db_avis.utilisateur_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="vous n'êtes pas l'auteur de cet avis")
    avis_crud.delete_avis(db, avis_id)
    return {"detail": "avis supprimé"}
