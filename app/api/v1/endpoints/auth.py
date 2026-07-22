from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services import auth_service
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenWithRefresh,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenWithRefresh, summary="Se connecter (email + mot de passe)")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, payload.email, payload.mot_de_passe)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="email ou mot de passe incorrect")
    return result


@router.post(
    "/refresh",
    response_model=TokenWithRefresh,
    summary="Obtenir un nouveau access token (rotation : l'ancien refresh token est révoqué)",
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    result = auth_service.refresh_acces_token(db, payload.refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token invalide, expiré ou déjà utilisé")
    return result


@router.post("/logout", summary="Révoquer un refresh token (déconnexion)")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    auth_service.logout(db, payload.refresh_token)
    return {"detail": "déconnecté"}


@router.post("/forgot-password", summary="Demander un lien de réinitialisation de mot de passe")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.request_password_reset(db, payload.email)
    return {"detail": "si cet email existe, un lien de réinitialisation a été envoyé"}


@router.post("/reset-password", summary="Réinitialiser le mot de passe avec le token reçu par email")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    success = auth_service.reset_password(db, payload.token, payload.nouveau_mot_de_passe)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token invalide ou expiré")
    return {"detail": "mot de passe réinitialisé avec succès"}
