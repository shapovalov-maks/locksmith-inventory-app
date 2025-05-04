# populate_known_codes.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Настройка SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Модель для таблицы known_codes
class KnownCode(Base):
    __tablename__ = 'known_codes'
    id = Column(Integer, primary_key=True)
    barcode = Column(String, nullable=False, unique=True)
    type = Column(String)
    description = Column(String)
    brand = Column(String)

# Примеры данных
codes = [
    {"barcode": "XH123456", "type": "universal", "description": "Xhorse Universal Remote", "brand": "Xhorse"},
    {"barcode": "KEYDIY-B04", "type": "universal", "description": "KEYDIY B04 Remote", "brand": "KEYDIY"},
    {"barcode": "AU112233", "type": "chip", "description": "Autel Chip 4D63", "brand": "Autel"},
    {"barcode": "TOY-TOY43", "type": "blade", "description": "TOY43 Blade for Toyota", "brand": "Aftermarket"},
    {"barcode": "FCC-GQ43VT20T", "type": "fcc", "description": "Honda Remote GQ43VT20T", "brand": "OEM"},
]

# Добавление в базу
for c in codes:
    existing = session.query(KnownCode).filter_by(barcode=c["barcode"]).first()
    if not existing:
        new_code = KnownCode(**c)
        session.add(new_code)

session.commit()
print("Code samples added successfully.")
