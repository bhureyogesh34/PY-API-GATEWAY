from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from auth import authenticate_user, create_access_token
from database import get_user
from pydantic import BaseModel
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: LoginForm):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}