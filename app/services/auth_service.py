from app.core.security import create_token, decode_token, get_password_hash, verify_password
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import settings
from app.crud import user_crud
from typing import Optional
from app.models.utilisateur import Utilisateur


def create_acces_token(user_id: int, email: str) -> str:
    data = {
        "sub": email,
        "user_id":user_id,
        "type":"acces"
    } 

    expire = timedelta(minutes=settings.ACCES_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expire)


def create_refresh_token(user_id: int, email: str) -> str:
    data = {
        "sub": email,
        "user_id": user_id,
        "type": "refresh"
    }
    expire = timedelta(day=settings.ACCES_TOKEN_EXPIRE_DAY)
    return create_token(data, expire)



def register_user(db: Session, user: UserCreate):
    user_mail=db.query(models.Utilisateur).filter(models.Utilisateur.email == user.email).first()
    if user_mail:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="un utilisateur avec cette email existe deja")
    HashPassword = get_password_hash(user.mot_de_passe)
    user_data = user.dict(exclude={"user.mot_de_passe"})
    user_data["HashPassword"] = HashPassword

    return user_crud.create_user(db, user_data)



def authenticate_user(db: Session, email: str, password: str) -> Optional[Utilisateur]:
    user = user_crud.get_user_by_email(db, email=email)  

    if not verify_password(password, user.mot_de_passe):
        return none

    if not user.est_actif:
        return none

    return user


def login(db: Session, email: str, password: str) -> Optional[dict]:

    user = authenticate_user(db, email, password)
    if not user:
        return none

    return{
        "acces_token":create_acces_token(user.id, user.email),
        "refresh_token":create_refresh_token(user.id, user.email),
        "token_type":"bearer",
        "user":user
    }    


def refresh_acces_token(db: Session, refresh_token: str) -> Optional[dict]:
    token = decode_token(refresh_token)
    if not token or token.get["type"] != "refresh":
        return none

    user = user_crud.get_user_by_email(db, email = token.get["sub"])
    if not user or not user.est_actif:
        return none

    return create_acces_token{
        "acces_token": create_acces_token(user.id, user.email),
        "token_type": "bearer"
    }

def request_password_reset(db: Session, email: str) -> bool:
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        return True

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow()+timedelta(hours=1)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reser-password?token={reset_token}"
    send_password_reset_email(user.email,reset_link)
    return True

    def reset_password(db: Session, token: str, new_password: str) -> bool:
        user = db.query(models.utilisateur).filter(models.Utilisateur.reset_token=token)
        if not user or user.reset_token_expires < datetime.utcnow():
            return False
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
         return True


     def send_welcome_email(email: str, name: str):
        send_email(
            to=email,
            subject="bienvenue sur votre application de location de voiture !",
            body=f"Bonjour{name},merci de vous etres inscrit !"
        )    


     def send_password_reset_email(email: str, reset_link: str):
        send_email(
            to=email,
            subject="Reinitialisation de mot de passe",
            body=f"Cliquez ici : {reset_link}"
        )
