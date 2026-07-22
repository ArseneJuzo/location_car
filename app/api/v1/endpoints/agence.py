from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud import agence_crud
from app.schemas.agence import AgenceRead, AgenceCreate, AgenceUpdate
from app.core.dependencies import get_db
from app.middlewares.auth_middleware import require_role
from app.models.utilisateur import Utilisateur, RoleUtilisateur

router = APIRouter(prefix="/agences", tags=["Agences"])


def _check_owner_or_admin(db: Session, agence_id: int, current_user: Utilisateur):
    db_agence = agence_crud.get_agence(db, agence_id)
    if current_user.role == RoleUtilisateur.administrateur:
        return db_agence
    if db_agence.responsable_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="vous ne gérez pas cette agence")
    return db_agence


@router.post(
    "/",
    response_model=AgenceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer son agence (rôle agence, une seule par responsable) ou pour un tiers (administrateur)",
)
def create_agence(
    agence: AgenceCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    if current_user.role == RoleUtilisateur.agence:
        if agence_crud.get_agence_by_responsable(db, current_user.id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vous gérez déjà une agence")
        agence.responsable_id = current_user.id
    return agence_crud.create_agence(db, agence)


@router.get(
    "/",
    response_model=List[AgenceRead],
    summary="Lister les agences (public) — passer lat/lon(/radius_km) pour trier par proximité",
)
def list_agences(
    skip: int = 0,
    limit: int = 10,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: float = 50,
    db: Session = Depends(get_db),
):
    if lat is not None and lon is not None:
        return agence_crud.get_agences_near(db, lat, lon, radius_km, limit)
    return agence_crud.get_all_agences(db, skip, limit)


@router.get("/{agence_id}", response_model=AgenceRead, summary="Détail d'une agence (public)")
def get_agence(agence_id: int, db: Session = Depends(get_db)):
    return agence_crud.get_agence(db, agence_id)


@router.put("/{agence_id}", response_model=AgenceRead, summary="Modifier son agence (responsable ou administrateur)")
def update_agence(
    agence_id: int,
    agence_update: AgenceUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    _check_owner_or_admin(db, agence_id, current_user)
    return agence_crud.update_agence(db, agence_id, agence_update)


@router.delete("/{agence_id}", status_code=status.HTTP_200_OK, summary="Supprimer son agence (responsable ou administrateur)")
def delete_agence(
    agence_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    _check_owner_or_admin(db, agence_id, current_user)
    agence_crud.delete_agence(db, agence_id)
    return {"detail": "agence supprimée"}
