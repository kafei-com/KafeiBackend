# app/db/database.py

from sqlmodel import SQLModel, create_engine, Session
from app.models.user import User  # REQUIRED
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    # echo=True,        # logs SQL (turn off later)
    pool_pre_ping=True
)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
