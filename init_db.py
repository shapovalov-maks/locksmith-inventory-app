from models import Base, engine

# Создание всех таблиц, определённых в models.py
Base.metadata.create_all(bind=engine)

print("✅ PostgreSQL database initialized with SQLAlchemy.")
