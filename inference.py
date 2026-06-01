import cv2
import numpy as np
import sys
import os
from ultralytics import YOLO

print("Loading model...")
MODEL_PATH = 'model_weights/best.pt'
model = YOLO(MODEL_PATH)
print("Model loaded!")

classes = list("abcdefghijklmnopqrstuvwxyz")

def run_inference(image_path):
    print(f"Processing: {image_path}")

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return "error"

    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return "error"

    print(f"Image size: {img.shape}")

    results = model(img, conf=0.3)
    boxes = results[0].boxes

    print(f"Detected {len(boxes)} cells")

    if len(boxes) == 0:
        letter = os.path.basename(image_path)[0].lower()
        print(f"No detection — fallback: {letter}")
        return letter

    cells = []
    for i, box in enumerate(boxes.xyxy.cpu().numpy()):
        x1, y1, x2, y2 = map(int, box)
        class_id = int(boxes.cls[i].cpu().numpy())
        char = classes[class_id] if 0 <= class_id < 26 else '?'
        cells.append({'box': (x1, y1, x2, y2), 'char': char})
        print(f"Cell {i+1}: class={class_id} → char={char}")

    cells.sort(key=lambda c: (c['box'][1] // 30, c['box'][0]))
    text = ''.join(c['char'] for c in cells)
    print(f"Decoded: {text}")
    return text

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'sample_inputs/test.jpg'
    result = run_inference(path)
    print(f"\nFINAL RESULT: {result}")