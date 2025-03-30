from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas
from ..database import get_db
from typing import List
from ..dependencies import oauth2_scheme

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return database.create_user(db, user)


@router.patch("/{user_id}", response_model=schemas.User)
def modify_user(user_id: str, user: schemas.UserModify, db: Session = Depends(database.get_db), current_user=Depends(oauth2_scheme)):
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this user")
    return database.modify_user(db, user_id, user)


@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user=Depends(oauth2_scheme)):
    return database.get_users(db, skip, limit)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: str, db: Session = Depends(database.get_db), current_user=Depends(oauth2_scheme)):
    return database.get_user(db, user_id)
