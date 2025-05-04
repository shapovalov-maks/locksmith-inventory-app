import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    session_token = Column(String)
    keys = relationship("Key", back_populates="user")


class Key(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    fcc_id = Column(String)
    barcode = Column(String)
    type = Column(String, default='fcc')  # fcc, universal, chip, blade, etc.
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    box_slot = Column(String)
    quantity = Column(Integer, default=0)
    available = Column(Boolean, default=True)
    comments = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="keys")


class KnownCode(Base):
    __tablename__ = 'known_codes'
    id = Column(Integer, primary_key=True)
    barcode = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # blade, chip, universal, etc.
    description = Column(String, nullable=False)
    brand = Column(String, nullable=True)
