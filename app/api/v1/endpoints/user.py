from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.crud import user_crud
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.core.dependencies import get_db
from app.services import auth_service
from app.middlewares.auth_middleware import require_role, get_current_user
from app.models.utilisateur import Utilisateur, RoleUtilisateur

router = APIRouter(prefix="/users", tags=["Users"])


def _check_self_or_admin(user_id: int, current_user: Utilisateur):
    if current_user.role != RoleUtilisateur.administrateur and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="accès non autorisé")


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="S'inscrire (client ou agence) — le tout premier compte créé devient administrateur",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db=db, user=user)


@router.get("/", response_model=List[UserRead], summary="Lister tous les utilisateurs (administrateur uniquement)")
def list_user(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_role(RoleUtilisateur.administrateur)),
):
    return user_crud.get_all_user(db=db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead, summary="Consulter un profil (soi-même ou administrateur)")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    _check_self_or_admin(user_id, current_user)
    return user_crud.get_user(db=db, user_id=user_id)


@router.put("/{user_id}", response_model=UserRead, summary="Modifier un profil (soi-même ou administrateur)")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    _check_self_or_admin(user_id, current_user)
    return user_crud.update_user(db, user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Supprimer un compte (soi-même ou administrateur)")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    _check_self_or_admin(user_id, current_user)
    user_crud.delete_user(db, user_id)
    return {"detail": "utilisateur supprimé"}
