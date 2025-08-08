import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_text TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_plate(plate_text):
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO plates (plate_text, timestamp) VALUES (?, ?)',
                   (plate_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
