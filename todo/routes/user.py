from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Todos, Users
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import SessionLocal
from jose import jwt,JWTError
from passlib.context import CryptContext

from .auth import verifytoken,bcrypt_context

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


router = APIRouter(
    prefix="/User",
    tags=["user"]
)

def get_db():
    db=SessionLocal()
    try:
        yield db;
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(verifytoken)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/profile',status_code=status.HTTP_200_OK)
async def profile(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="not authorized")
    db_user = db.get(Users, user.get("user_id"))
    return db_user

@router.put("/password",status_code=status.HTTP_204_NO_CONTENT)
async def changePassword(user:user_dependency, db:db_dependency,user_verification:UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Error on password change')

    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/phone/{phone_number}",status_code=status.HTTP_204_NO_CONTENT)
async def updatePhone(user:user_dependency,db:db_dependency,phone_number:str):
    if user is None:
            raise HTTPException(status_code=401, detail='Error on password change')

    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()

