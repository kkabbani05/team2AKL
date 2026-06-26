from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.database import Base, create_database_session

router = APIRouter()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class UserCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str

class UserRead(UserCreate):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: int


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
        raise HTTPException(status_code=422, detail={"description": "Player not found"})
    

