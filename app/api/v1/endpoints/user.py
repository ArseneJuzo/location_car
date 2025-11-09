from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.crud import user_crud
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.core.dependencies import get_db
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)

def create_user(user:UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db=db, user=user)

@router.get("/", response_model=List[UserRead])

def list_user(skip: int = 0, limit: int = 10, db: Session=Depends(get_db)):
    return user_crud.get_all_user(db=db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model= UserRead)

def get_user(user_id:int, db: Session = Depends(get_db)):
    return user_crud.get_user(db=db, user_id=user_id)


@router.put("/{user_id}", response_model=UserRead)

def update_user(user_id: int, user_update: UserUpdate, db: Session=Depends(get_db)):
    return user_crud.update_user(db, user_id, user_update)


@router.delete("/{user_id}",response_model=UserRead)

def delete_user(user_id:int, db: Session=Depends(get_db)):
    return user_crud.delete_user(db, user_id)