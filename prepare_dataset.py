import os, shutil, random
from pathlib import Path

# Change this to where your Braille Dataset folder actually is
SOURCE = r"C:\Users\HP\Downloads\archive (2)\Braille Dataset\Braille Dataset"

TRAIN_IMG = "dataset/images/train"
VAL_IMG   = "dataset/images/val"
TRAIN_LBL = "dataset/labels/train"
VAL_LBL   = "dataset/labels/val"

for p in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    os.makedirs(p, exist_ok=True)

classes = list("abcdefghijklmnopqrstuvwxyz")

images = [f for f in os.listdir(SOURCE) 
          if f.lower().endswith('.jpg') or f.lower().endswith('.png')]
random.shuffle(images)

split = int(len(images) * 0.8)
train_imgs = images[:split]
val_imgs   = images[split:]

def make_label(filename, dest_lbl_folder):
    letter = filename[0].lower()
    if letter not in classes:
        return
    class_id = classes.index(letter)
    label = f"{class_id} 0.5 0.5 1.0 1.0\n"
    label_name = Path(filename).stem + ".txt"
    with open(os.path.join(dest_lbl_folder, label_name), 'w') as f:
        f.write(label)

for img in train_imgs:
    shutil.copy(os.path.join(SOURCE, img), os.path.join(TRAIN_IMG, img))
    make_label(img, TRAIN_LBL)

for img in val_imgs:
    shutil.copy(os.path.join(SOURCE, img), os.path.join(VAL_IMG, img))
    make_label(img, VAL_LBL)

print(f"Train: {len(train_imgs)} images")
print(f"Val:   {len(val_imgs)} images")
print("Dataset ready!")