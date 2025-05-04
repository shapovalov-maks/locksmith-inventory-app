from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    with conn.begin():
        conn.execute(text("ALTER TABLE keys ADD COLUMN IF NOT EXISTS barcode TEXT"))
        conn.execute(text("ALTER TABLE keys ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'fcc'"))

print("✅ Columns 'barcode' and 'type' added to PostgreSQL.")
