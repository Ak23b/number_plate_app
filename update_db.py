import sqlite3
import os

# Path to your existing DB on Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
db_path = os.path.join(desktop_path, "plates.db")

# Connect to the DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Try adding the new column
try:
    cursor.execute("ALTER TABLE plates ADD COLUMN image_path TEXT;")
    conn.commit()
    print(f"✅ Column 'image_path' added successfully in {db_path}")
except sqlite3.OperationalError:
    print(f"ℹ️ Column 'image_path' already exists in {db_path}")

conn.close()
