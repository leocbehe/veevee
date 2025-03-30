from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from . import schemas, database, models
from sqlalchemy.orm import Session
from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def hash_user_password(user: models.User):
    """
    Hash the user's password using bcrypt before storing.
    
    Args:
        user (models.User): The user object with a plain text password to be hashed.
    
    Returns:
        models.User: The user object with the password replaced by its bcrypt hash.
    """
    user.password = get_password_hash(user.password)
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token with optional custom expiration.
    
    Args:
        data (dict): Payload data to be encoded in the token
        expires_delta (timedelta, optional): Custom token expiration time. 
            If not provided, uses default ACCESS_TOKEN_EXPIRE_MINUTES.
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        user = database.get_user(user_id)
        return user
    except JWTError:
        raise credentials_exception