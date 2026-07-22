from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models
from app.schemas.paiement import PaiementCreate


def create_paiement(db: Session, paiement: PaiementCreate):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == paiement.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="réservation non trouvée")
    if reservation.paiement:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cette réservation a déjà un paiement")

    db_paiement = models.Paiement(
        reservation_id=paiement.reservation_id,
        montant=paiement.montant,
        methode=paiement.methode,
        statut="en_attente",
    )

    db.add(db_paiement)
    db.commit()
    db.refresh(db_paiement)
    return db_paiement


def get_paiement(db: Session, paiement_id: int):
    paiement = db.query(models.Paiement).filter(models.Paiement.id == paiement_id).first()
    if not paiement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="paiement non trouvé")
    return paiement


def update_statut(db: Session, paiement_id: int, statut: str):
    db_paiement = get_paiement(db, paiement_id)
    db_paiement.statut = statut
    db.commit()
    db.refresh(db_paiement)
    return db_paiement
