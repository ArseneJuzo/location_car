from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status

from app import models
from app.models.vehicule import StatutVehicule
from app.schemas import vehicule as vehicule_schemas


def create_vehicule(db: Session, vehicule: vehicule_schemas.VehiculeCreate, agence_id: int):
    data = vehicule.dict(exclude={"agence_id"})
    db_vehicule = models.Vehicule(**data, agence_id=agence_id)

    db.add(db_vehicule)

    agence = db.query(models.Agence).filter(models.Agence.id == agence_id).first()
    if agence:
        agence.nombre_vehicule_total = (agence.nombre_vehicule_total or 0) + 1
        agence.nombre_vehicule_disponibles = (agence.nombre_vehicule_disponibles or 0) + 1

    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


def get_vehicule(db: Session, vehicule_id: int):
    vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="véhicule non trouvé")
    return vehicule


def get_all_vehicules(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    agence_id: Optional[int] = None,
    categorie: Optional[str] = None,
    statut: Optional[str] = None,
):
    query = db.query(models.Vehicule)
    if agence_id is not None:
        query = query.filter(models.Vehicule.agence_id == agence_id)
    if categorie is not None:
        query = query.filter(models.Vehicule.categorie == categorie)
    if statut is not None:
        query = query.filter(models.Vehicule.statut == statut)
    return query.offset(skip).limit(limit).all()


def update_vehicule(db: Session, vehicule_id: int, vehicule_update: vehicule_schemas.VehiculeUpdate):
    db_vehicule = get_vehicule(db, vehicule_id)
    update_data = vehicule_update.dict(exclude_unset=True)

    nouveau_statut = update_data.get("statut")
    if nouveau_statut is not None and nouveau_statut != db_vehicule.statut:
        # en_location est piloté uniquement par le cycle de vie des réservations
        if StatutVehicule.en_location in (nouveau_statut, db_vehicule.statut):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="le statut en_location est géré par les réservations (confirmer / terminer / annuler)",
            )
        agence = db.query(models.Agence).filter(models.Agence.id == db_vehicule.agence_id).first()
        if agence:
            if nouveau_statut == StatutVehicule.disponible:
                agence.nombre_vehicule_disponibles = (agence.nombre_vehicule_disponibles or 0) + 1
            else:
                agence.nombre_vehicule_disponibles = max((agence.nombre_vehicule_disponibles or 1) - 1, 0)

    for key, value in update_data.items():
        setattr(db_vehicule, key, value)

    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


def set_vehicule_image(db: Session, vehicule_id: int, image_url: str):
    db_vehicule = get_vehicule(db, vehicule_id)
    db_vehicule.image_url = image_url
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


def delete_vehicule(db: Session, vehicule_id: int):
    db_vehicule = get_vehicule(db, vehicule_id)

    if db.query(models.Reservation).filter(models.Reservation.vehicule_id == vehicule_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer un véhicule ayant un historique de réservations",
        )

    agence = db.query(models.Agence).filter(models.Agence.id == db_vehicule.agence_id).first()
    if agence:
        agence.nombre_vehicule_total = max((agence.nombre_vehicule_total or 1) - 1, 0)
        if db_vehicule.statut == StatutVehicule.disponible:
            agence.nombre_vehicule_disponibles = max((agence.nombre_vehicule_disponibles or 1) - 1, 0)

    db.delete(db_vehicule)
    db.commit()
    return db_vehicule
