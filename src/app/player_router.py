from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import create_database_session
from app.models import User, UserCreate, UserRead

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=201)
def register_user(user: UserCreate, session: Session = Depends(create_database_session)):
    username = user.name.strip().lower()
    if len(username) == 0:
        raise HTTPException(status_code=422, detail="Name cannot be empty")

    all_users = session.query(User).all()
    for db_user in all_users:
        if username == db_user.name.strip().lower():
            raise HTTPException(status_code=422, detail="Username is already taken")

    new_db_user = User(**user.model_dump())
    session.add(new_db_user)
    session.commit()
    session.refresh(new_db_user)
    return new_db_user

@router.get("/", response_model=list[UserRead])
def get_registered_users(session: Session = Depends(create_database_session)):
    return session.query(User).all()

