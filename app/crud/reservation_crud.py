from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models
from app.models.vehicule import StatutVehicule
from app.models.reservation import StatutReservation
from app.schemas.reservation import ReservationCreate

# statuts qui bloquent le véhicule sur leur période
STATUTS_ACTIFS = (StatutReservation.en_attente, StatutReservation.confirmée)

# transitions autorisées ; annulée et terminée sont des états finaux
TRANSITIONS_AUTORISEES = {
    StatutReservation.en_attente: {StatutReservation.confirmée, StatutReservation.annulée},
    StatutReservation.confirmée: {StatutReservation.terminée, StatutReservation.annulée},
    StatutReservation.annulée: set(),
    StatutReservation.terminée: set(),
}


def _get_vehicule_verrouille(db: Session, vehicule_id: int):
    # verrou de ligne (SELECT ... FOR UPDATE) : sérialise les réservations
    # concurrentes sur un même véhicule
    return db.query(models.Vehicule).filter(models.Vehicule.id == vehicule_id).with_for_update().first()


def _liberer_vehicule(db: Session, vehicule):
    if vehicule and vehicule.statut == StatutVehicule.en_location:
        vehicule.statut = StatutVehicule.disponible
        agence = db.query(models.Agence).filter(models.Agence.id == vehicule.agence_id).first()
        if agence:
            agence.nombre_vehicule_disponibles = (agence.nombre_vehicule_disponibles or 0) + 1


def create_reservation(db: Session, reservation: ReservationCreate, utilisateur_id: int):
    vehicule = _get_vehicule_verrouille(db, reservation.vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="véhicule non trouvé")
    if vehicule.statut != StatutVehicule.disponible:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="le véhicule n'est pas disponible")
    if reservation.date_fin <= reservation.date_debut:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="la date de fin doit être postérieure à la date de début")

    chevauchement = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.vehicule_id == reservation.vehicule_id,
            models.Reservation.statut.in_(STATUTS_ACTIFS),
            models.Reservation.date_debut < reservation.date_fin,
            models.Reservation.date_fin > reservation.date_debut,
        )
        .first()
    )
    if chevauchement:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="le véhicule est déjà réservé sur tout ou partie de cette période",
        )

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
    ancien_statut = db_reservation.statut

    if nouveau_statut not in TRANSITIONS_AUTORISEES[ancien_statut]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"transition de statut interdite : {ancien_statut.value} -> {nouveau_statut.value}",
        )

    vehicule = _get_vehicule_verrouille(db, db_reservation.vehicule_id)

    if nouveau_statut == StatutReservation.confirmée:
        if not vehicule or vehicule.statut != StatutVehicule.disponible:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="le véhicule n'est pas disponible, impossible de confirmer la réservation",
            )
        vehicule.statut = StatutVehicule.en_location
        agence = db.query(models.Agence).filter(models.Agence.id == vehicule.agence_id).first()
        if agence:
            agence.nombre_vehicule_disponibles = max((agence.nombre_vehicule_disponibles or 1) - 1, 0)
            agence.nombre_reservation = (agence.nombre_reservation or 0) + 1
    elif ancien_statut == StatutReservation.confirmée:
        # confirmée -> annulée / terminée : le véhicule redevient disponible
        _liberer_vehicule(db, vehicule)

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

    if db_reservation.statut == StatutReservation.confirmée:
        _liberer_vehicule(db, _get_vehicule_verrouille(db, db_reservation.vehicule_id))

    db.delete(db_reservation)
    db.commit()
    return db_reservation
