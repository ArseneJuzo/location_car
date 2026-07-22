from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models
from app.schemas.avis import AvisCreate


def create_avis(db: Session, avis: AvisCreate, utilisateur_id: int):
    vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == avis.vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="véhicule non trouvé")

    db_avis = models.Avis(
        utilisateur_id=utilisateur_id,
        vehicule_id=avis.vehicule_id,
        note=avis.note,
        commentaire=avis.commentaire,
    )

    db.add(db_avis)
    db.commit()
    db.refresh(db_avis)
    return db_avis


def get_avis(db: Session, avis_id: int):
    avis = db.query(models.Avis).filter(models.Avis.id == avis_id).first()
    if not avis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="avis non trouvé")
    return avis


def get_avis_by_vehicule(db: Session, vehicule_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Avis)
        .filter(models.Avis.vehicule_id == vehicule_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_avis(db: Session, avis_id: int):
    db_avis = get_avis(db, avis_id)
    db.delete(db_avis)
    db.commit()
    return db_avis
