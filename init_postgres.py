from urllib.parse import urlparse
import psycopg2

DATABASE_URL = "postgresql://locksmith_inventory_user:GkcYCmnSAOAYjZqz74mXlXl39kAq5clL@dpg-d0b69feuk2gs73ceele0-a.oregon-postgres.render.com/locksmith_inventory"

result = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    dbname=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    session_token TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS keys (
    id SERIAL PRIMARY KEY,
    fcc_id TEXT NOT NULL,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    box_slot TEXT,
    quantity INTEGER DEFAULT 0,
    available BOOLEAN DEFAULT TRUE,
    comments TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS key_models (
    id SERIAL PRIMARY KEY,
    key_id INTEGER NOT NULL REFERENCES keys(id),
    make TEXT,
    model TEXT,
    year_start INTEGER,
    year_end INTEGER
)
''')

conn.commit()
conn.close()

print("✅ PostgreSQL database initialized.")
