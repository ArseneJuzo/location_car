from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import decode_token
from app.models.utilisateur import Utilisateur, RoleUtilisateur

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if payload.get("type") != "acces":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="type de token invalide")

    user_id = payload.get("user_id")
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first() if user_id is not None else None
    if not user or not user.est_actif:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="utilisateur invalide ou inactif")

    return user


def require_role(*roles: RoleUtilisateur):
    def dependency(current_user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="vous n'avez pas les droits pour effectuer cette action",
            )
        return current_user

    return dependency
