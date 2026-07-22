from typing import Optional

from sqlalchemy.orm import Session
from app import models
from app.schemas import agence as agence_schemas
from app.utils.geo import haversine_km
from fastapi import HTTPException, status


def create_agence(db: Session, agence: agence_schemas.AgenceCreate):
    db_agence = models.Agence(**agence.dict())

    db.add(db_agence)
    db.commit()
    db.refresh(db_agence)

    return db_agence


def get_agence(db: Session, agence_id: int):
    agence_by_id = db.query(models.Agence).filter(models.Agence.id == agence_id).first()
    if not agence_by_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agence non existante")

    return agence_by_id


def get_agence_by_responsable(db: Session, responsable_id: int):
    return db.query(models.Agence).filter(models.Agence.responsable_id == responsable_id).first()


def get_all_agences(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Agence).offset(skip).limit(limit).all()


def get_agences_near(db: Session, lat: float, lon: float, radius_km: float, limit: int = 10):
    """Agences ayant des coordonnées, triées par distance croissante au point donné."""
    candidates = db.query(models.Agence).filter(
        models.Agence.latitude.isnot(None), models.Agence.longitude.isnot(None)
    ).all()

    resultats = []
    for agence in candidates:
        distance = haversine_km(lat, lon, agence.latitude, agence.longitude)
        if distance <= radius_km:
            agence.distance_km = round(distance, 2)
            resultats.append(agence)

    resultats.sort(key=lambda a: a.distance_km)
    return resultats[:limit]


def update_agence(db: Session, agence_id: int, agence_update: agence_schemas.AgenceUpdate):
    db_agence = get_agence(db, agence_id)
    for key, value in agence_update.dict(exclude_unset=True).items():
        setattr(db_agence, key, value)

    db.commit()
    db.refresh(db_agence)

    return db_agence


def delete_agence(db: Session, agence_id: int):
    db_agence = get_agence(db, agence_id)

    if db.query(models.Vehicule).filter(models.Vehicule.agence_id == agence_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer une agence ayant des véhicules enregistrés",
        )

    db.delete(db_agence)
    db.commit()
    return db_agence
