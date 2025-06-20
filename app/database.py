#!/usr/bin/env python3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cambia los valores según tu docker-compose.yml y tus datos reales
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:abc123@mysql:3306/appdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    provincia = Column(String(50), nullable=True)
    concello = Column(String(50), nullable=True)  # <-- Añadido este campo
    foto_perfil = Column(String(300), nullable=True)
    edad = Column(Integer, nullable=True)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
