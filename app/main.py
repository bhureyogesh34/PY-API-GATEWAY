 # FastAPI app

# main.py
from fastapi import FastAPI, Depends, HTTPException, Request,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated
from . import models, schemas, auth
from .database import SessionLocal, engine
from .services import route_request
from .dependencies import get_db
from .config import settings
from sqlalchemy import or_

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User registration endpoint
@app.post("/register", response_model=schemas.UserInDB)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists in a single query
    existing_user = db.query(models.User).filter(
        or_(
            models.User.username == user.username,
            models.User.email == user.email
        )
    ).first()

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        else:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authentication endpoint
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected API Gateway endpoint
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(
    service_name: str,
    path: str,
    request: Request,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Add user information to headers for downstream services
    headers = dict(request.headers)
    headers["X-User-ID"] = str(current_user.id)
    headers["X-User-Roles"] = "admin" if current_user.is_superuser else "user"
    
    return await route_request(service_name, path, request.method, headers, await request.body())