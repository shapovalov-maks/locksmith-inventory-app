import csv
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, FccCode, FccModel

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def import_fcc_codes(file_path):
    session = SessionLocal()
    added_fcc_codes = 0
    added_fcc_models = 0
    skipped = 0

    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            fcc_id = row.get("FCCid", "").strip().upper()
            make = row.get("Make", "").strip()
            model = row.get("Model", "").strip()
            year = row.get("Year", "").strip()
            description = f"{make} {model} {year}".strip()

            if not fcc_id:
                print(f"⚠️ Row {i}: Missing FCC ID. Skipping.")
                skipped += 1
                continue

            # Add or reuse existing FCC code
            fcc_code = session.query(FccCode).filter_by(fcc_id=fcc_id).first()
            if not fcc_code:
                fcc_code = FccCode(fcc_id=fcc_id, description=description)
                session.add(fcc_code)
                session.flush()
                added_fcc_codes += 1

            # Add model info
            fcc_model = FccModel(
                fcc_code_id=fcc_code.id,
                make=make,
                model=model,
                year=year
            )
            session.add(fcc_model)
            added_fcc_models += 1

            if i % 500 == 0:
                print(f"📦 Processed {i} rows...")

        session.commit()
        session.close()

    print(f"\n✅ Import complete.\n➡️ FCC Codes added: {added_fcc_codes}\n➡️ FCC Models added: {added_fcc_models}\n⚠️ Skipped (missing FCC ID): {skipped}")

if __name__ == '__main__':
    import_fcc_codes('car_fcc_info_DB.csv')
