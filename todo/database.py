from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:akash@localhost/todofastapi'

# engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})
engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False,bind=engine)

Base = declarative_base()