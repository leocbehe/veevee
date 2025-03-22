import sqlalchemy
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from . import models, dependencies, schemas
from .config import settings

load_dotenv()
db_hostname = os.getenv("db_hostname")
db_port = os.getenv("db_port")
db_password = os.getenv("db_password")
db_username = os.getenv("db_username")
db_name = os.getenv("db_name")

DB_URL = f"postgresql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}"

engine = sqlalchemy.create_engine(DB_URL)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, username, password):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not dependencies.verify_password(password, user.password):
        return False
    return user

# User-related database functions
def create_user(db: Session, user):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(**user.model_dump())
    db_user = dependencies.hash_user_password(db_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def modify_user(db: Session, user_id: str, user):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"No user found with the ID {user_id}")
    for k, v in user.model_dump(exclude_unset=True).items():
        setattr(db_user, k, v)
    db_user = dependencies.hash_user_password(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user