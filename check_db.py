import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

print("🔍 All keys in 'keys' table:")
cursor.execute("SELECT id, fcc_id FROM keys")
for row in cursor.fetchall():
    print(row)

print("\n🔍 All key-model links in 'key_models' table:")
cursor.execute("SELECT * FROM key_models")
for row in cursor.fetchall():
    print(row)

conn.close()
