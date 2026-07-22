from app.core.security import create_token, decode_token, get_password_hash, verify_password
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.core.config import settings
from app.crud import user_crud
from typing import Optional
from app.models.utilisateur import Utilisateur, RoleUtilisateur
from app.models.refresh_token import RefreshToken
from app.utils.email import send_email
import secrets
import uuid


def create_acces_token(user_id: int, email: str) -> str:
    data = {
        "sub": email,
        "user_id": user_id,
        "type": "acces"
    }

    expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expire)


def create_refresh_token(db: Session, user_id: int, email: str) -> str:
    jti = uuid.uuid4().hex
    expire = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAY)
    expires_at = datetime.utcnow() + expire

    db.add(RefreshToken(jti=jti, utilisateur_id=user_id, expires_at=expires_at))
    db.commit()

    data = {
        "sub": email,
        "user_id": user_id,
        "type": "refresh",
        "jti": jti,
    }
    return create_token(data, expire)


def register_user(db: Session, user: UserCreate):
    user_mail = user_crud.get_user_by_email(db, email=user.email)
    if user_mail:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="un utilisateur avec cette email existe deja")

    # le tout premier compte créé sur l'instance devient administrateur (bootstrap) ;
    # ensuite l'auto-inscription ne peut jamais accorder le rôle administrateur.
    if user_crud.count_users(db) == 0:
        role = RoleUtilisateur.administrateur
    elif user.role == RoleUtilisateur.administrateur:
        role = RoleUtilisateur.client
    else:
        role = user.role

    user_data = user.dict(exclude={"mot_de_passe", "role"})
    user_data["hashed_password"] = get_password_hash(user.mot_de_passe)
    user_data["role"] = role

    db_user = user_crud.create_user(db, user_data)
    send_welcome_email(db_user.email, db_user.nom_complet)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[Utilisateur]:
    user = user_crud.get_user_by_email(db, email=email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.est_actif:
        return None

    return user


def login(db: Session, email: str, password: str) -> Optional[dict]:
    user = authenticate_user(db, email, password)
    if not user:
        return None

    return {
        "acces_token": create_acces_token(user.id, user.email),
        "refresh_token": create_refresh_token(db, user.id, user.email),
        "token_type": "bearer",
        "user": user
    }


def refresh_acces_token(db: Session, refresh_token: str) -> Optional[dict]:
    """Valide le refresh token, le révoque, et en émet un nouveau (rotation).

    La rotation empêche la réutilisation d'un refresh token volé : dès qu'il
    sert une fois, il devient invalide, un nouveau doit être utilisé.
    """
    try:
        token = decode_token(refresh_token)
    except ValueError:
        return None

    if not token or token.get("type") != "refresh":
        return None

    jti = token.get("jti")
    db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first() if jti else None
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        return None

    user = user_crud.get_user_by_email(db, email=token.get("sub"))
    if not user or not user.est_actif:
        return None

    db_token.revoked = True
    db.commit()

    return {
        "acces_token": create_acces_token(user.id, user.email),
        "refresh_token": create_refresh_token(db, user.id, user.email),
        "token_type": "bearer",
    }


def logout(db: Session, refresh_token: str) -> None:
    """Révoque le refresh token fourni (idempotent, ne révèle rien si déjà invalide)."""
    try:
        token = decode_token(refresh_token)
    except ValueError:
        return

    jti = token.get("jti")
    if not jti:
        return

    db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if db_token:
        db_token.revoked = True
        db.commit()


def request_password_reset(db: Session, email: str) -> bool:
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        return True

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    send_password_reset_email(user.email, reset_link)
    return True


def reset_password(db: Session, token: str, new_password: str) -> bool:
    user = db.query(Utilisateur).filter(Utilisateur.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
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
        body=f"Bonjour {name}, merci de vous etre inscrit !"
    )


def send_password_reset_email(email: str, reset_link: str):
    send_email(
        to=email,
        subject="Reinitialisation de mot de passe",
        body=f"Cliquez ici : {reset_link}"
    )
