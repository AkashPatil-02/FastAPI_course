from fastapi import Depends, FastAPI
import models
from database import engine
from routes import auth,todo,admin


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
