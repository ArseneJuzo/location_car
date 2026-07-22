from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserUpdate
from fastapi import HTTPException, status
from app.core.security import get_password_hash


def create_user(db: Session, user_data: dict):
    db_user = models.Utilisateur(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user(db: Session, user_id: int):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="utilisateur non trouvé")
    return user


def get_all_user(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Utilisateur).offset(skip).limit(limit).all()


def count_users(db: Session) -> int:
    return db.query(models.Utilisateur).count()


def get_user_by_email(db: Session, email: str):
    return db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)

    update_data = user_update.dict(exclude_unset=True)
    mot_de_passe = update_data.pop("mot_de_passe", None)
    if mot_de_passe:
        db_user.hashed_password = get_password_hash(mot_de_passe)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)

    if db.query(models.Reservation).filter(models.Reservation.utilisateur_id == user_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer un utilisateur ayant un historique de réservations",
        )
    if db.query(models.Agence).filter(models.Agence.responsable_id == user_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer un utilisateur responsable d'une agence",
        )
    if db.query(models.Avis).filter(models.Avis.utilisateur_id == user_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="impossible de supprimer un utilisateur ayant laissé des avis",
        )

    db.delete(db_user)
    db.commit()
    return db_user
