import torch
import cv2
import easyocr
import sqlite3
import os
from datetime import datetime

# Paths
image_path = 'samples/test4.jpeg'
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
db_path = os.path.join(desktop_path, "plates.db")
weights_path = 'weights/best.pt'

# Load YOLOv5 model (locally)
model = torch.hub.load('yolov5', 'custom', path=weights_path, source='local')
model.conf = 0.5

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# Ensure image exists
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found: {image_path}")
img = cv2.imread(image_path)
img_draw = img.copy()

# Connect to SQLite database
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS plates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_text TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Ensure image_path column exists
cursor.execute("PRAGMA table_info(plates)")
columns = [col[1] for col in cursor.fetchall()]
if "image_path" not in columns:
    cursor.execute("ALTER TABLE plates ADD COLUMN image_path TEXT;")
    conn.commit()
    print("✅ Added missing column 'image_path' to plates table.")

# Run YOLOv5 detection
results = model(img)
detections = results.xyxy[0].numpy()

if len(detections) == 0:
    print("No plate detected.")
else:
    for i, det in enumerate(detections):
        x1, y1, x2, y2, conf, cls = map(int, det[:6])
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)

        crop = img[y1:y2, x1:x2]

        # Optional: Add padding to the crop
        PAD = 10
        h, w = crop.shape[:2]
        x_pad = max(0, x1 - PAD)
        y_pad = max(0, y1 - PAD)
        x2_pad = min(img.shape[1], x2 + PAD)
        y2_pad = min(img.shape[0], y2 + PAD)
        crop_padded = img[y_pad:y2_pad, x_pad:x2_pad]

        # OCR with padding
        ocr_result = reader.readtext(crop_padded)

        # Combine all detected text strings
        plate_text = ' '.join([text[1] for text in ocr_result]).upper().strip()

        if plate_text:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_filename = f"result_{plate_text}_{timestamp}.jpg"
            output_path = os.path.join("output", output_filename)
            os.makedirs("output", exist_ok=True)

            # Save annotated image
            cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_draw, plate_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imwrite(output_path, img_draw)

            # Save to DB with image path
            cursor.execute(
                'INSERT INTO plates (plate_text, timestamp, image_path) VALUES (?, ?, ?)',
                (plate_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), output_path)
            )
            conn.commit()

            print(f"[{i+1}] Detected plate: {plate_text}")
            print(f"💾 DB updated at: {db_path}")
            print(f"🖼  Annotated image saved as: {output_path}")
        else:
            print(f"[{i+1}] Plate detected, but OCR failed.")

conn.close()
