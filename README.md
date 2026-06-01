# 👁️ BrailleVision AI

**Bridging the accessibility gap with real-time Braille-to-Text & Audio translation.**

BrailleVision AI is a dual-engine computer vision platform designed to translate physical Braille (embossed or handwritten) into digital text and auditory speech. Built for the BrailleVision Hackathon 2026.

## 🚀 Features
* **Omni-Channel Input:** Live Camera streaming, Image upload, and Video frame analysis.
* **Custom AI Model:** Trained YOLOv8 object detection for 26 Braille cell classes.
* **Deterministic Fallback:** OpenCV geometric Hough Circle detection for challenging lighting conditions.
* **Spatial Text Reconstruction:** Custom algorithm to sort detected letters into proper, readable sentences.
* **Native Audio:** Integrated Text-to-Speech (TTS) for instant auditory feedback.

---

## 🛠️ Tech Stack
* **Frontend:** React.js, HTML5 Canvas, WebRTC
* **Backend:** Python 3.12, Flask, Flask-CORS
* **Machine Learning:** PyTorch, Ultralytics YOLOv8
* **Computer Vision:** OpenCV, NumPy

---

## 💻 How to Run Locally

### Prerequisites
Make sure you have **Python 3.12+** and **Node.js** installed on your machine. 

### 1. Backend Setup (Python/Flask)
Open a terminal and navigate to the root directory of the project.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install the required Python packages
pip install flask flask-cors gtts ultralytics opencv-python

# Start the Flask API server
python app.py
```
### 2. Frontend Setup (React)
Open a second terminal and navigate to the frontend folder.

```bash
# Move into the frontend directory
cd frontend

# Install Node dependencies
npm install axios

# Start the React development server
npm start
```
