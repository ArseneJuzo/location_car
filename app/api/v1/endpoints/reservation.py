from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import reservation_crud, agence_crud
from app.schemas.reservation import ReservationRead, ReservationCreate, ReservationUpdateStatut
from app.models.reservation import StatutReservation
from app.core.dependencies import get_db
from app.middlewares.auth_middleware import require_role, get_current_user
from app.models.utilisateur import Utilisateur, RoleUtilisateur

router = APIRouter(prefix="/reservations", tags=["Reservations"])


def _agence_of(db: Session, current_user: Utilisateur):
    return agence_crud.get_agence_by_responsable(db, current_user.id)


def _check_access(db: Session, reservation, current_user: Utilisateur):
    if current_user.role == RoleUtilisateur.administrateur:
        return
    if current_user.role == RoleUtilisateur.client and reservation.utilisateur_id == current_user.id:
        return
    if current_user.role == RoleUtilisateur.agence:
        agence = _agence_of(db, current_user)
        if agence and reservation.vehicule and reservation.vehicule.agence_id == agence.id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="accès non autorisé à cette réservation")


@router.post(
    "/",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Réserver un véhicule disponible (rôle client)",
)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.client)),
):
    return reservation_crud.create_reservation(db, reservation, current_user.id)


@router.get(
    "/",
    response_model=List[ReservationRead],
    summary="Lister ses réservations (client : les siennes, agence : celles de son parc, admin : toutes)",
)
def list_reservations(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role == RoleUtilisateur.administrateur:
        return reservation_crud.get_all_reservations(db, skip, limit)
    if current_user.role == RoleUtilisateur.agence:
        agence = _agence_of(db, current_user)
        if not agence:
            return []
        return reservation_crud.get_reservations_for_agence(db, agence.id, skip, limit)
    return reservation_crud.get_reservations_for_client(db, current_user.id, skip, limit)


@router.get("/{reservation_id}", response_model=ReservationRead, summary="Détail d'une réservation (parties concernées)")
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    reservation = reservation_crud.get_reservation(db, reservation_id)
    _check_access(db, reservation, current_user)
    return reservation


@router.patch(
    "/{reservation_id}/statut",
    response_model=ReservationRead,
    summary="Confirmer / terminer / annuler une réservation (agence propriétaire ou administrateur)",
)
def update_statut(
    reservation_id: int,
    payload: ReservationUpdateStatut,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.agence, RoleUtilisateur.administrateur)),
):
    reservation = reservation_crud.get_reservation(db, reservation_id)
    _check_access(db, reservation, current_user)
    return reservation_crud.update_statut(db, reservation_id, payload.statut)


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_200_OK,
    summary="Annuler/supprimer une réservation (client : uniquement si en_attente ; agence/admin : toujours)",
)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    reservation = reservation_crud.get_reservation(db, reservation_id)
    _check_access(db, reservation, current_user)
    if current_user.role == RoleUtilisateur.client and reservation.statut != StatutReservation.en_attente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="seule une réservation en attente peut être annulée par le client")
    reservation_crud.delete_reservation(db, reservation_id)
    return {"detail": "réservation supprimée"}
