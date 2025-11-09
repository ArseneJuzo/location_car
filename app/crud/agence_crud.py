from sqlalchemy.orm import session
from app import models, schemas
from fastapi import HTTPException, status


def create_agence(db: session, agence:schemas.Agencecreate):
    db_agence = models.Agence(
        nom = agence.nom
        ville = agence.ville
        pays = agence.pays
        telephone = agence.telephone
        email = agence.email
        mot_de_passe = agence.mot_de_passe

    )

    db.add(db_agence)
    db.commit()
    db.refresh()

    return db_agence


 def get_agence(db: session, agence_id: int):
    agence_by_id = db.query(models.Agence).filter(models.Agence.id == agence_id).first()
    if not agence_by_id:
        raise HTTPException(Status_code=status.HTTP_404_NOT_FOUND, detail="agence non existante")

    return agence_by_id

 def update_agence(db: session, agence_id: int, agence_update: schemas.AgenceUpdate):
    db_agence = get_agence(db, agence_id)
    for key ,value in agengce_update.dict(exclude_unset=True).items():
        setattr(db_agence, key, value)

        db.commit()
        db.refresh(db_agence)

        return db_agence


def delete_agence(db: session, agence_id: int):
    db_agence = get_agence(db, agence_id)
    db.delete(db_agence)
    db.commit()
    return {"message":}


       