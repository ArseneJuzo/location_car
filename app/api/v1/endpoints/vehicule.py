from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud import vehicule_crud, agence_crud
from app.schemas.vehicule import VehiculeRead, VehiculeCreate, VehiculeUpdate
from app.core.dependencies import get_db
from app.middlewares.auth_middleware import require_role
from app.models.utilisateur import Utilisateur, RoleUtilisateur
from app.utils.storage import save_vehicule_image

router = APIRouter(prefix="/vehicules", tags=["Vehicules"])


def _resolve_agence_id(db: Session, vehicule: VehiculeCreate, current_user: Utilisateur) -> int:
    if current_user.role == RoleUtilisateur.administrateur:
        if not vehicule.agence_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agence_id requis pour un administrateur")
        return vehicule.agence_id

    agence = agence_crud.get_agence_by_responsable(db, current_user.id)
    if not agence:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vous ne gérez aucune agence")
    return agence.id


def _check_owner_or_admin(db: Session, vehicule_id: int, current_user: Utilisateur):
    db_vehicule = vehicule_crud.get_vehicule(db, vehicule_id)
    if current_user.role == RoleUtilisateur.administrateur:
        return db_vehicule

    agence = agence_crud.get_agence_by_responsable(db, current_user.id)
    if not agence or agence.id != db_vehicule.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="vous ne gérez pas ce véhicule")
    return db_vehicule


@router.post(
    "/",
    response_model=VehiculeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un véhicule au parc de son agence (rôle agence ou administrateur)",
)
def create_vehicule(
    vehicule: VehiculeCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    agence_id = _resolve_agence_id(db, vehicule, current_user)
    return vehicule_crud.create_vehicule(db, vehicule, agence_id)


@router.get("/", response_model=List[VehiculeRead], summary="Rechercher des véhicules (public, filtres agence/catégorie/statut)")
def list_vehicules(
    skip: int = 0,
    limit: int = 10,
    agence_id: Optional[int] = None,
    categorie: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return vehicule_crud.get_all_vehicules(db, skip, limit, agence_id, categorie, statut)


@router.get("/{vehicule_id}", response_model=VehiculeRead, summary="Détail d'un véhicule (public)")
def get_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    return vehicule_crud.get_vehicule(db, vehicule_id)


@router.put("/{vehicule_id}", response_model=VehiculeRead, summary="Modifier un véhicule (agence propriétaire ou administrateur)")
def update_vehicule(
    vehicule_id: int,
    vehicule_update: VehiculeUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    _check_owner_or_admin(db, vehicule_id, current_user)
    return vehicule_crud.update_vehicule(db, vehicule_id, vehicule_update)


@router.post(
    "/{vehicule_id}/photo",
    response_model=VehiculeRead,
    summary="Téléverser la photo d'un véhicule (agence propriétaire ou administrateur, jpeg/png/webp, 5 Mo max)",
)
def upload_vehicule_photo(
    vehicule_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    db_vehicule = _check_owner_or_admin(db, vehicule_id, current_user)
    image_url = save_vehicule_image(file, previous_url=db_vehicule.image_url)
    return vehicule_crud.set_vehicule_image(db, vehicule_id, image_url)


@router.delete("/{vehicule_id}", status_code=status.HTTP_200_OK, summary="Retirer un véhicule (agence propriétaire ou administrateur)")
def delete_vehicule(
    vehicule_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    _check_owner_or_admin(db, vehicule_id, current_user)
    vehicule_crud.delete_vehicule(db, vehicule_id)
    return {"detail": "véhicule supprimé"}
