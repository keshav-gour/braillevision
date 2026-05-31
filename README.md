# BrailleVision AI
### Real-time Braille to Text and Speech Converter

An AI-powered accessibility application that uses a camera to detect 
physical Braille labels in real time, decode them into English text, 
and read them aloud for visually impaired users.

**Built for BrailleVision Hackathon 2026**

## Tech Stack
- YOLOv8 Nano — Braille cell detection
- OpenCV — image preprocessing + dot grid analysis  
- Flask — REST API backend
- React.js — frontend UI
- pyttsx3 — offline text to speech

## How to Run
pip install -r requirements.txt
python app.py