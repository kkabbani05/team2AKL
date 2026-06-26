from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import create_database_session
from app.models import User, UserCreate, UserRead

router = APIRouter()

@router.post("/", response_model=UserRead)
def attempt_login(user: UserCreate, session: Session = Depends(create_database_session)):
    username = user.name.strip().lower()
    found_user = False
    all_users = session.query(User).all()
    for db_user in all_users:
        db_username = db_user.name.strip().lower()
        if username == db_username:
            found_user = True
            return db_user
    if not found_user:
        raise HTTPException(status_code=422, detail="Player not found")
    
@router.get("/", response_model=list[UserRead])
def get_registered_users(session: Session = Depends(create_database_session)):
    return session.query(User).all()