from fastapi import APIRouter, HTTPException, Depends
from database import get_db, create_user
from auth import get_password_hash, get_current_active_user
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    scopes: str = ""

class UserResponse(BaseModel):
    id: str
    username: str
    disabled: bool
    scopes: List[str]

@router.post("/register", response_model=dict)
def register_user(user: UserCreate):
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    cursor.execute('SELECT username FROM users WHERE username = ?', (user.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_id = create_user(user.username, hashed_password, user.scopes)
    return {"message": "User created successfully", "user_id": user_id}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: dict = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
def get_all_users(current_user: dict = Depends(get_current_active_user)):
    if "admin" not in current_user.scopes:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username, disabled, scopes FROM users')
    users = [
        {
            "id": row[0],
            "username": row[1],
            "disabled": bool(row[2]),
            "scopes": row[3].split(',') if row[3] else []
        }
        for row in cursor.fetchall()
    ]
    return users