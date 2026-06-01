from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({'status': 'BrailleVision API running!'})

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    f = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}.jpg')
    f.save(path)
    
    # Use inference pipeline
    try:
        from inference import run_inference
        text = run_inference(path)
    except Exception as e:
        text = f"Pipeline error: {str(e)}"
    
    return jsonify({'text': text})

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'status': 'done'})

if __name__ == '__main__':
    print("Starting BrailleVision backend...")
    print("API running at http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)