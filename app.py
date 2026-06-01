from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, base64

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods=["GET","POST","OPTIONS"])

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/')
def home():
    return jsonify({
        'status': 'BrailleVision AI running!',
        'supported_inputs': [
            'live_camera', 'recorded_video', 'uploaded_image',
            'handwritten_braille', 'embossed_braille',
            'sentence_recognition', 'page_recognition'
        ]
    })

def save_image_from_request():
    print(f"Content-Type: {request.content_type}")
    print(f"Files: {list(request.files.keys())}")
    print(f"Is JSON: {request.is_json}")

    # Method 1 — file upload
    if request.files and 'image' in request.files:
        f = request.files['image']
        path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}.jpg')
        f.save(path)
        print(f"Saved file upload: {path}")
        return path

    # Method 2 — base64 JSON
    if request.is_json:
        data = request.get_json(silent=True)
        if data and 'image_base64' in data:
            b64 = data['image_base64']
            if ',' in b64:
                b64 = b64.split(',')[1]
            try:
                img_bytes = base64.b64decode(b64)
                path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}.jpg')
                with open(path, 'wb') as f:
                    f.write(img_bytes)
                print(f"Saved base64: {path}")
                return path
            except Exception as e:
                print(f"Base64 decode error: {e}")
                return None

    # Method 3 — raw body
    if request.data:
        try:
            path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}.jpg')
            with open(path, 'wb') as f:
                f.write(request.data)
            print(f"Saved raw data: {path}")
            return path
        except Exception as e:
            print(f"Raw data error: {e}")
            return None

    print("No image found in request!")
    return None

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    print("\n--- New prediction request ---")
    try:
        path = save_image_from_request()

        if not path:
            print("ERROR: No image in request")
            return jsonify({
                'error': 'No image provided',
                'success': False
            }), 400

        print(f"Processing image: {path}")

        input_type = 'uploaded_image'
        if request.is_json:
            data = request.get_json(silent=True)
            if data:
                input_type = data.get('input_type', 'uploaded_image')

        from inference import run_inference
        text = run_inference(path)
        print(f"Result: {text}")

        if os.path.exists(path):
            os.remove(path)

        return jsonify({
            'text': text,
            'success': True,
            'input_type': input_type,
            'characters_detected': len([c for c in text if c.isalpha()])
        })

    except Exception as e:
        print(f"ERROR in predict: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/predict_video', methods=['POST', 'OPTIONS'])
def predict_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    try:
        import cv2
        if 'video' not in request.files:
            return jsonify({'error': 'No video provided'}), 400

        f = request.files['video']
        video_path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4()}.mp4')
        f.save(video_path)

        cap = cv2.VideoCapture(video_path)
        results = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % 30 == 0:
                frame_path = os.path.join(UPLOAD_FOLDER, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_path, frame)
                from inference import run_inference
                text = run_inference(frame_path)
                if text and text != '?' and text != 'error':
                    results.append(text)
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            frame_count += 1

        cap.release()
        if os.path.exists(video_path):
            os.remove(video_path)

        final_text = ' '.join(set(results)) if results else 'No Braille detected'
        return jsonify({
            'text': final_text,
            'success': True,
            'frames_processed': frame_count
        })

    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/speak', methods=['POST', 'OPTIONS'])
def speak():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    text = request.json.get('text', '') if request.is_json else ''
    try:
        from gtts import gTTS
        import tempfile, time
        tts = gTTS(
            text=f"The Braille text reads: {text}",
            lang='en',
            tld='co.in'
        )
        # Unique filename to avoid conflicts
        tmp_path = os.path.join(UPLOAD_FOLDER, f'speech_{uuid.uuid4()}.mp3')
        tts.save(tmp_path)
        os.system(f'start /min {tmp_path}')
        return jsonify({'status': 'done'})
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("BrailleVision AI Backend Starting...")
    print("API: http://0.0.0.0:5000")
    print("Supported: camera, video, image, handwritten, embossed, sentence, page")
    app.run(debug=False, port=5000, host='0.0.0.0')