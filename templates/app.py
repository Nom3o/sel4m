from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
import dlib
import os
from gtts import gTTS

app = Flask(__name__)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
stored_face = None

def process_image(image_data):
    image_data = image_data.split(',')[1]
    img = base64.b64decode(image_data)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img

def is_blinking(landmarks):
    left_eye_ratio = (landmarks[41][1] - landmarks[37][1]) / (landmarks[39][0] - landmarks[36][0])
    right_eye_ratio = (landmarks[46][1] - landmarks[43][1]) / (landmarks[45][0] - landmarks[42][0])
    return left_eye_ratio > 0.25 and right_eye_ratio > 0.25

def is_mouth_open(landmarks):
    mouth_ratio = (landmarks[66][1] - landmarks[62][1]) / (landmarks[54][0] - landmarks[48][0])
    return mouth_ratio > 0.3

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/capture', methods=['POST'])
def capture():
    global stored_face
    image_data = request.json['image']
    img = process_image(image_data)
    faces = detector(img, 1)
    if faces:
        shape = predictor(img, faces[0])
        stored_face = np.array([[p.x, p.y] for p in shape.parts()])
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/recognize', methods=['POST'])
def recognize():
    image_data = request.json['image']
    img = process_image(image_data)
    faces = detector(img, 1)
    if faces:
        shape = predictor(img, faces[0])
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        if stored_face is not None and np.linalg.norm(stored_face - landmarks) < 1000:
            tts = gTTS(text="Hello, user!", lang='en')
            tts.save('static/greeting.mp3')
            return jsonify(success=True, greeting='/static/greeting.mp3')
    return jsonify(success=False)

@app.route('/liveness_check', methods=['POST'])
def liveness_check():
    instruction = request.json['instruction']
    image_data = request.json['image']
    img = process_image(image_data)
    faces = detector(img, 1)
    if faces:
        shape = predictor(img, faces[0])
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        if instruction == 'blink_your_eyes' and is_blinking(landmarks):
            return jsonify(success=True)
        elif instruction == 'open_your_mouth' and is_mouth_open(landmarks):
            return jsonify(success=True)
    return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True)
