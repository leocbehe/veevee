from sqlalchemy.orm import Session
from fastapi.security import (
    OAuth2PasswordRequestForm
)
from .. import schemas
from .. import database
from ..config import settings
from .. import dependencies
from datetime import (
    datetime,
    timezone,
    timedelta,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    user_login: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    """
    Generate a new access token for authenticated user.

    Authenticates user credentials and creates a time-limited access token.
    Raises an HTTPException if authentication fails.

    Args:
        user_login (OAuth2PasswordRequestForm): User login credentials
        db (Session): Database session for user authentication

    Returns:
        schemas.Token: A response containing JWT access token and token type
    """
    user = database.authenticate_user(
        db,
        user_login.username,
        user_login.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_issued = (datetime.now(timezone.utc)).timestamp()
    access_token_expires = (
        datetime.now(timezone.utc) + timedelta(minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    ).timestamp()
    access_token = dependencies.create_access_token(
        data={
            "sub": str(user.user_id),
            "username": user.username,
            "issued_at": int(access_token_issued),
            "expires_at": int(access_token_expires),
        },
    )
    
    # Return the token in the format defined by the schema
    return schemas.Token(access_token=access_token, token_type="bearer")