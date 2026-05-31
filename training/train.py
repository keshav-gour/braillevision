import os
os.chdir('..')  # go to braillevision/ root

from ultralytics import YOLO

print("Starting training...")
print("Loading model...")

model = YOLO('yolov8n.pt')

print("Model loaded! Starting training now...")
print("This will take 20-40 minutes on CPU...")

results = model.train(
    data='C:/Users/HP/OneDrive/Desktop/braillevision/dataset/data.yaml',
    epochs=50,
    imgsz=640,
    batch=8,
    name='braille_v1',
    project='runs/detect',
    patience=10,
    lr0=0.01,
    device='cpu'
)

print("Training complete!")
print("Weights saved to: runs/detect/braille_v1/weights/best.pt")