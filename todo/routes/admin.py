from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..models import Todos, Users
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import SessionLocal
from jose import jwt,JWTError

from .auth import verifytoken,bcrypt_context



router = APIRouter(
    prefix="/Admin",
    tags=["admin"]
)

def get_db():
    db=SessionLocal()
    try:
        yield db;
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(verifytoken)]


@router.get('/alltodos')
async def allTodos(user:user_dependency,db:db_dependency):
    if user is None or user.get("role")!="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="not authorized")

    todos = db.query(Todos).all()
    return todos


@router.delete('/deletetodo/{user_id}/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def deleteTodo(Adminuser:user_dependency,db:db_dependency,user_id:int,todo_id:int):
    if Adminuser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if Adminuser.get("role")!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    todo = db.query(Todos).filter(Todos.id==todo_id).filter(Todos.user_id==user_id).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No todo exists")
    db.delete(todo)
    db.commit()


@router.get("/users",status_code=status.HTTP_200_OK)
async def getUsers(db:db_dependency, user:user_dependency):
        if user is None or user.get("role")!="admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        users = db.query(Users).all()
        return users


@router.post("/changepassword",status_code=status.HTTP_204_NO_CONTENT)
async def changeuserPassword(db:db_dependency,user:user_dependency, user_id:int, password:str):
    if user is None or user.get("role")!="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = db.query(Users).filter(user_id==Users.id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

    new_hashed_password = bcrypt_context.hash(password)
    user.hashed_password = new_hashed_password
    db.add(user)
    db.commit()