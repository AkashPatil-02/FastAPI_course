from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path,status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import TodoModel, Todos
from .auth import verifytoken


router = APIRouter(
    prefix="/Todo",
    tags=["todo"]
)

def get_db():
    db=SessionLocal()
    try:
        yield db;
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(verifytoken)]


@router.get("/")
async def readAll(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authorized")
    return db.query(Todos).filter(user.get("user_id")==Todos.user_id).all()

@router.get("/{todo_id}")
async def getTodo(user:user_dependency,db:db_dependency, todo_id:int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authenticated")
    
    todo_model = db.query(Todos).filter(Todos.id==todo_id).filter(user.get('user_id')==Todos.user_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="Todo not found")

@router.post("/",status_code=status.HTTP_200_OK)
async def addTodo(user: user_dependency,db:db_dependency,todo_item:TodoModel):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authenticated")
    
    item = Todos(**todo_item.model_dump(), user_id = user.get('user_id'))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/update/{item_id}")
async def updateTodo(user:user_dependency,db:db_dependency,item:TodoModel,item_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authenticated")
    todo_model = db.query(Todos).filter(Todos.id==item_id).filter(Todos.user_id==user.get("user_id")).first()
    if todo_model is not None:
        todo_model.title = item.title
        todo_model.description = item.description
        todo_model.complete = item.complete
        todo_model.priority = item.priority

        db.add(todo_model)
        db.commit()
        return todo_model
    raise HTTPException(status_code=404,detail="item not found")

@router.delete("/delete/{item_id}")
async def deleteTodo(user:user_dependency,db:db_dependency,item_id:int = Path(gt=0)):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authenticated")
    todo_item = db.query(Todos).filter(Todos.id==item_id).filter(user.get("user_id")==Todos.user_id).first()
    if todo_item is not None:
        db.delete(todo_item)
        db.commit()
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404,detail="not found")