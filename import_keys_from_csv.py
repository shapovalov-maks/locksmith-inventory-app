import csv
import sqlite3

def import_keys_from_csv(csv_file_path):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            fcc_id = row['fcc_id'].strip().upper()
            make = row['make'].strip()
            model = row['model'].strip()
            year = int(row['year'])
            box_slot = row.get('box_slot', '').strip()
            quantity = int(row.get('quantity', 0))
            comments = row.get('comments', '').strip()
            available = 1 if quantity > 0 else 0

            # Проверка: существует ли уже такой FCC ID
            cursor.execute('SELECT id FROM keys WHERE fcc_id = ?', (fcc_id,))
            existing = cursor.fetchone()

            if existing:
                key_id = existing[0]
                # Обновим данные
                cursor.execute('''
                    UPDATE keys
                    SET quantity = quantity + ?, box_slot = ?, available = CASE WHEN quantity + ? > 0 THEN 1 ELSE 0 END, comments = ?
                    WHERE fcc_id = ?
                ''', (quantity, box_slot, quantity, comments, fcc_id))
            else:
                # Создание нового ключа
                cursor.execute('''
                    INSERT INTO keys (fcc_id, make, model, year, box_slot, quantity, available, comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (fcc_id, make, model, year, box_slot, quantity, available, comments))
                key_id = cursor.lastrowid

            # Добавим в таблицу моделей
            cursor.execute('''
                INSERT INTO key_models (key_id, make, model, year_start, year_end)
                VALUES (?, ?, ?, ?, ?)
            ''', (key_id, make, model, year, year))

    conn.commit()
    conn.close()
    print("✅ Импорт завершён успешно.")

# 👉 Пример использования:
# import_keys_from_csv('keys.csv')
