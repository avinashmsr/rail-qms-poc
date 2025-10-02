from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/qms")
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)