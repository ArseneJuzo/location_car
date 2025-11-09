from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserRead, UserCreate, UserUpdate
from fastapi import HTTPException, status
from app.core.security import get_password_hash



def create_user(db: Session, user:UserCreate):
   
    db_user = models.Utilisateur(
            nom_complet = user.nom_complet,
            telephone = user.telephone,
            email = user.email,
            mot_de_passe = user.mot_de_passe
        )
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
        
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="utilisateur non trouvé")
    return user



def get_all_user(db: Session, skip:int = 0, limit:int = 0):
    return db.query(models.Utilisateur).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str):
    user_by_email = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
    if not user_by_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="aucun utilisateur avec cette email existant")
    return user_by_email    


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    
    db.delete(db_user)
    db.commit()
    return{""}
