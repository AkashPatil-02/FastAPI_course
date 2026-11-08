from fastapi import Depends, FastAPI
from .models import Base
from .database import engine
from .routes import auth,todo,admin,user


app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():   
    return {'status':'ok'}

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(user.router)