from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
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
    fcc_id = Column(String, nullable=True)
    barcode = Column(String)
    type = Column(String, default='fcc')
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
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    brand = Column(String, nullable=True)


class FccCode(Base):
    __tablename__ = 'fcc_codes'
    id = Column(Integer, primary_key=True)
    fcc_id = Column(String, unique=True, nullable=False)
    description = Column(String)

    models = relationship("FccModel", back_populates="fcc_code", cascade="all, delete")


class FccModel(Base):
    __tablename__ = 'fcc_models'
    id = Column(Integer, primary_key=True)
    fcc_code_id = Column(Integer, ForeignKey('fcc_codes.id'), nullable=False)
    make = Column(String)
    model = Column(String)
    year = Column(String)

    fcc_code = relationship("FccCode", back_populates="models")
