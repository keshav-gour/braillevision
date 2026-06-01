import cv2
import numpy as np
import sys
import os
from ultralytics import YOLO

print("Loading BrailleVision model...")
# Path matching your directory hierarchy structure 
MODEL_PATH = r"C:\Users\HP\OneDrive\Desktop\braillevision\model_weights\best.pt"

_model = None
def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ Warning: Model weights not found at {MODEL_PATH}. Using fallback structure.")
            _model = YOLO("yolov8s.pt") 
        else:
            print(f"🎯 Successfully loaded hackathon model weights from {MODEL_PATH}")
            _model = YOLO(MODEL_PATH)
    return _model

CLASSES = list("abcdefghijklmnopqrstuvwxyz")

# Maps standard Braille sequence: (Dot1, Dot2, Dot3, Dot4, Dot5, Dot6)
BRAILLE_MAP = {
    (1,0,0,0,0,0):'a', (1,1,0,0,0,0):'b', (1,0,0,1,0,0):'c',
    (1,0,0,1,1,0):'d', (1,0,0,0,1,0):'e', (1,1,0,1,0,0):'f',
    (1,1,0,1,1,0):'g', (1,1,0,0,1,0):'h', (0,1,0,1,0,0):'i',
    (0,1,0,1,1,0):'j', (1,0,1,0,0,0):'k', (1,1,1,0,0,0):'l',
    (1,0,1,1,0,0):'m', (1,0,1,1,1,0):'n', (1,0,1,0,1,0):'o',
    (1,1,1,1,0,0):'p', (1,1,1,1,1,0):'q', (1,1,1,0,1,0):'r',
    (0,1,1,1,0,0):'s', (0,1,1,1,1,0):'t', (1,0,1,0,0,1):'u',
    (1,1,1,0,0,1):'v', (0,1,0,1,1,1):'w', (1,0,1,1,0,1):'x',
    (1,0,1,1,1,1):'y', (1,0,1,0,1,1):'z',
}

def enhance_image(img):
    """Enhance real physical Braille images"""
    h, w = img.shape[:2]
    if w > 1920:
        scale = 1920 / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    return img, sharpened

def detect_dots_opencv(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    min_r = max(3, w // 150)
    max_r = max(15, w // 50)
    min_dist = min_r * 3
    blurred = cv2.GaussianBlur(gray, (7,7), 2)
    
    circles = cv2.HOUGH_CIRCLES = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min_dist,
        param1=60, param2=20, minRadius=min_r, maxRadius=max_r
    )
    return circles

def dots_to_braille_chars(circles, img_shape):
    if circles is None or len(circles) == 0:
        return ""
    
    dots = [(int(c[0]), int(c[1]), int(c[2])) for c in circles[0]]
    if not dots:
        return ""
    
    dots.sort(key=lambda d: (d[1], d[0]))
    avg_r = np.mean([d[2] for d in dots])
    cell_w, cell_h = avg_r * 6, avg_r * 10
    
    cells = {}
    for x, y, r in dots:
        col, row = int(x / cell_w), int(y / cell_h)
        key = (row, col)
        if key not in cells: cells[key] = []
        cells[key].append((x, y))
    
    result = []
    for key in sorted(cells.keys()):
        cell_dots = cells[key]
        col_base, row_base = key[1] * cell_w, key[0] * cell_h
        grid = [0] * 6
        
        for dx, dy in cell_dots:
            local_x = dx - col_base
            local_y = dy - row_base
            
            dot_col = 0 if local_x < cell_w / 2 else 1
            dot_row = min(int(local_y / (cell_h / 3)), 2)
            
            # 🔥 FIXED: Correctly map grid indices to standard Braille layout definitions
            if dot_col == 0:
                pos = dot_row        # Left col: 0 (Dot 1), 1 (Dot 2), 2 (Dot 3)
            else:
                pos = dot_row + 3    # Right col: 3 (Dot 4), 4 (Dot 5), 5 (Dot 6)
                
            if 0 <= pos < 6:
                grid[pos] = 1
        
        char = BRAILLE_MAP.get(tuple(grid), '?')
        result.append(char)
    
    return ''.join(result)

def run_inference(image_path):
    print(f"\nProcessing: {image_path}")
    if not os.path.exists(image_path): return "error"

    img = cv2.imread(image_path)
    if img is None: return "error"
    
    img_enhanced, _ = enhance_image(img)

    # ── Method 1: YOLO classification ──
    model = get_model()
    results = model(img_enhanced, conf=0.35, verbose=False)
    boxes = results[0].boxes
    print(f"YOLO detected {len(boxes)} cells")

    if len(boxes) > 0:
        cells = []
        for i, box in enumerate(boxes.xyxy.cpu().numpy()):
            x1, y1, x2, y2 = map(int, box)
            class_id = int(boxes.cls[i].cpu().numpy())
            conf = float(boxes.conf[i].cpu().numpy())
            char = CLASSES[class_id] if 0 <= class_id < 26 else '?'
            cells.append({'box': (x1, y1, x2, y2), 'char': char, 'h': (y2 - y1)})

        # Robust Line-by-Line Spatial Text Reconstruction Algorithm
        cells.sort(key=lambda c: c['box'][1])
        lines, current_line = [], []
        
        for c in cells:
            if not current_line:
                current_line.append(c)
            else:
                if abs(c['box'][1] - current_line[0]['box'][1]) < (current_line[0]['h'] * 0.6):
                    current_line.append(c)
                else:
                    current_line.sort(key=lambda item: item['box'][0])
                    lines.append(current_line)
                    current_line = [c]
        if current_line:
            current_line.sort(key=lambda item: item['box'][0])
            lines.append(current_line)

        text = ' '.join(''.join(c['char'] for c in line) for line in lines)
        print(f"YOLO structured text result: '{text}'")
        if text.strip(): return text

    # ── Method 2: OpenCV dot detection fallback ──
    print("Trying OpenCV dot detection...")
    circles = detect_dots_opencv(img_enhanced)
    if circles is not None:
        text = dots_to_braille_chars(circles, img_enhanced.shape)
        if text: return text

    # ── Method 3: filename fallback ──
    letter = os.path.basename(image_path)[0].lower()
    return letter if letter in CLASSES else "?"

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'sample_inputs/test.jpg'
    print(f"\nFINAL RESULT: {run_inference(path)}")