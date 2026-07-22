from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models
from app.models.vehicule import StatutVehicule
from app.models.reservation import StatutReservation
from app.schemas.reservation import ReservationCreate


def create_reservation(db: Session, reservation: ReservationCreate, utilisateur_id: int):
    vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == reservation.vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="véhicule non trouvé")
    if vehicule.statut != StatutVehicule.disponible:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="le véhicule n'est pas disponible")
    if reservation.date_fin <= reservation.date_debut:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="la date de fin doit être postérieure à la date de début")

    nb_jours = (reservation.date_fin - reservation.date_debut).days
    montant_total = nb_jours * vehicule.prix_journalier

    db_reservation = models.Reservation(
        utilisateur_id=utilisateur_id,
        vehicule_id=reservation.vehicule_id,
        date_debut=reservation.date_debut,
        date_fin=reservation.date_fin,
        montant_total=montant_total,
        statut=StatutReservation.en_attente,
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def get_reservation(db: Session, reservation_id: int):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="réservation non trouvée")
    return reservation


def get_reservations_for_client(db: Session, utilisateur_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Reservation)
        .filter(models.Reservation.utilisateur_id == utilisateur_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reservations_for_agence(db: Session, agence_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Reservation)
        .join(models.Vehicule, models.Reservation.vehicule_id == models.Vehicule.id)
        .filter(models.Vehicule.agence_id == agence_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_reservations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Reservation).offset(skip).limit(limit).all()


def update_statut(db: Session, reservation_id: int, nouveau_statut: StatutReservation):
    db_reservation = get_reservation(db, reservation_id)
    vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == db_reservation.vehicule_id).first()

    if nouveau_statut == StatutReservation.confirmée:
        if vehicule:
            vehicule.statut = StatutVehicule.en_location
        if vehicule:
            agence = db.query(models.Agence).filter(models.Agence.id == vehicule.agence_id).first()
            if agence:
                agence.nombre_vehicule_disponibles = max((agence.nombre_vehicule_disponibles or 1) - 1, 0)
                agence.nombre_reservation = (agence.nombre_reservation or 0) + 1
    elif nouveau_statut in (StatutReservation.annulée, StatutReservation.terminée):
        if vehicule and vehicule.statut == StatutVehicule.en_location:
            vehicule.statut = StatutVehicule.disponible
            agence = db.query(models.Agence).filter(models.Agence.id == vehicule.agence_id).first()
            if agence:
                agence.nombre_vehicule_disponibles = (agence.nombre_vehicule_disponibles or 0) + 1

    db_reservation.statut = nouveau_statut
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def delete_reservation(db: Session, reservation_id: int):
    db_reservation = get_reservation(db, reservation_id)

    if db_reservation.paiement is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer une réservation ayant un paiement associé",
        )

    db.delete(db_reservation)
    db.commit()
    return db_reservation
