import sqlite3
import os
import argparse

# Path to database (same central location as main.py)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
db_path = os.path.join(desktop_path, "plates.db")

# Parse arguments
parser = argparse.ArgumentParser(description="View or clear license plate detection history.")
parser.add_argument("--clear", action="store_true", help="Clear all history from the database.")
args = parser.parse_args()

# Check if DB exists
if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit()

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure image_path column exists for display
cursor.execute("PRAGMA table_info(plates)")
columns = [col[1] for col in cursor.fetchall()]
image_path_exists = "image_path" in columns

if args.clear:
    # Clear history but keep the file & structure
    cursor.execute("DELETE FROM plates")
    conn.commit()
    conn.close()
    print(f"🧹 History cleared. Database file still exists at: {db_path}")
    exit()

# Fetch all plate records sorted by timestamp DESC
cursor.execute("SELECT * FROM plates ORDER BY timestamp DESC")
records = cursor.fetchall()
conn.close()

# Display DB location
print(f"\n📂 Viewing history from database: {db_path}\n")

if not records:
    print("No plate records found.")
else:
    for record in records:
        plate_id = record[0]
        plate_text = record[1]
        timestamp = record[2]
        image_path = record[3] if image_path_exists else "N/A"

        print(f"ID: {plate_id}")
        print(f"   Plate: {plate_text}")
        print(f"   Timestamp: {timestamp}")
        print(f"   Annotated image: {image_path}")
        print("-" * 50)
