# init_db.py

import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Обновлённая таблица пользователей с session_token
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    session_token TEXT
)
''')

# Таблица ключей
cursor.execute('''
CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fcc_id TEXT NOT NULL,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    box_slot TEXT,
    quantity INTEGER DEFAULT 0,
    available INTEGER DEFAULT 1,
    comments TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Таблица моделей ключей (если используешь)
cursor.execute('''
CREATE TABLE IF NOT EXISTS key_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER NOT NULL,
    make TEXT,
    model TEXT,
    year_start INTEGER,
    year_end INTEGER,
    FOREIGN KEY(key_id) REFERENCES keys(id)
)
''')

conn.commit()
conn.close()

print("✅ Database initialized with session_token support.")
