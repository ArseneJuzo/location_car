from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import paiement_crud, reservation_crud, agence_crud
from app.schemas.paiement import PaiementRead, PaiementCreate, PaiementUpdateStatut
from app.core.dependencies import get_db
from app.middlewares.auth_middleware import require_role, get_current_user
from app.models.utilisateur import Utilisateur, RoleUtilisateur

router = APIRouter(prefix="/paiements", tags=["Paiements"])


def _check_access(db: Session, paiement, current_user: Utilisateur):
    if current_user.role == RoleUtilisateur.administrateur:
        return
    reservation = reservation_crud.get_reservation(db, paiement.reservation_id)
    if current_user.role == RoleUtilisateur.client and reservation.utilisateur_id == current_user.id:
        return
    if current_user.role == RoleUtilisateur.agence:
        agence = agence_crud.get_agence_by_responsable(db, current_user.id)
        if agence and reservation.vehicule and reservation.vehicule.agence_id == agence.id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="accès non autorisé à ce paiement")


@router.post(
    "/",
    response_model=PaiementRead,
    status_code=status.HTTP_201_CREATED,
    summary="Déclarer le paiement d'une réservation (montant en FCFA, rôle client)",
)
def create_paiement(
    paiement: PaiementCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.client)),
):
    reservation = reservation_crud.get_reservation(db, paiement.reservation_id)
    if reservation.utilisateur_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cette réservation ne vous appartient pas")
    return paiement_crud.create_paiement(db, paiement)


@router.get("/{paiement_id}", response_model=PaiementRead, summary="Détail d'un paiement (parties concernées)")
def get_paiement(
    paiement_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    paiement = paiement_crud.get_paiement(db, paiement_id)
    _check_access(db, paiement, current_user)
    return paiement


@router.patch(
    "/{paiement_id}/statut",
    response_model=PaiementRead,
    summary="Valider/rejeter un paiement (agence propriétaire ou administrateur)",
)
def update_statut(
    paiement_id: int,
    payload: PaiementUpdateStatut,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    paiement = paiement_crud.get_paiement(db, paiement_id)
    _check_access(db, paiement, current_user)
    return paiement_crud.update_statut(db, paiement_id, payload.statut)
