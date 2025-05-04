# check_fcc_count.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import FccCode
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

count = session.query(FccCode).count()
print(f"✅ Total FCC codes in database: {count}")
