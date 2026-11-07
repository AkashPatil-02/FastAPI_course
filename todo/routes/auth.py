from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Users
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from jose import jwt,JWTError


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRECT_KEY ='b9a20930a0aa62590417753cd587401408abc885f4bd08665c64886afd2bdacd'
ALGORITHM ='HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
ouath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/authenticateuser')



class createUserReq(BaseModel):
    username:str
    email:str
    firstname:str
    lastname:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db=SessionLocal()
    try:
        yield db;
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]


def authenticateUser(username:str,password:str,db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def createToken(username:str,user_id:int,role:str, expires_delta:timedelta):
    encode={"sub":username,"id":user_id,"role":role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRECT_KEY,algorithm=ALGORITHM)

async def verifytoken(token:Annotated[str,Depends(ouath2_bearer)]):
    try:
        payload = jwt.decode(token,SECRECT_KEY,algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        user_id:str = payload.get('id')
        role:str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate")

        return {"username":username,"user_id":user_id,"role":role}

    except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate")        
        



@router.post("/",status_code=status.HTTP_201_CREATED)
async def createUser(db:db_dependency,userdata:createUserReq):
    user = Users(
        email = userdata.email,
        username = userdata.username,
        firstname = userdata.firstname,
        lastname = userdata.lastname,
        role = userdata.role,
        hashed_password = bcrypt_context.hash(userdata.password),
        is_active = True
    )
    db.add(user)
    db.commit()


@router.post("/authenticateuser",response_model=Token)
async def authUser(db:db_dependency, form_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticateUser(form_data.username,form_data.password,db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate")


    token = createToken(user.username,user.id,user.role,timedelta(minutes=20))
    return {
        'access_token':token,
        'token_type':'bearer'
    }