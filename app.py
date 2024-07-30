from flask import Flask, request, render_template, send_file, jsonify
import logging
from datetime import datetime
import requests
import base64
import os
import uuid
import cv2
import numpy as np

app = Flask(__name__)

# Setup logging
logging.basicConfig(filename='honeypot.log', level=logging.INFO, format='%(message)s')

@app.route('/')
def index():
    log_request(request)
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        log_request(request, f'Sign-up attempt with email: {email}')
        return jsonify({"message": "Sign-up successful"}), 200

@app.route('/verify-phone', methods=['GET', 'POST'])
def verify_phone():
    if request.method == 'GET':
        return render_template('verify_phone.html')
    else:
        data = request.json
        phone_number = data.get('phoneNumber')
        log_request(request, f'Phone number submitted: {phone_number}')
        return jsonify({"message": "Phone verification successful"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    device_info = data.get('deviceInfo')
    ip_info = get_ip_info(request.remote_addr)
    log_request(request, f'Login attempt\nUsername: {username}\nPassword: {password}\nDevice Info: {device_info}\nIP Info: {ip_info}')
    if username == 'admin' and password == 'lalamia':
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/ceo-login', methods=['POST'])
def ceo_login():
    data = request.json
    username = data.get('ceoUsername')
    password = data.get('ceoPassword')
    if username == "allday" and password == "lastman":
        device_info = data.get('deviceInfo')
        ip_info = get_ip_info(request.remote_addr)
        log_request(request, f'CEO login\nUsername: {username}\nDevice Info: {device_info}\nIP Info: {ip_info}')
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid CEO credentials"}), 401

@app.route('/admin')
def admin():
    log_request(request)
    return render_template('admin_panel.html')

@app.route('/cmd', methods=['GET', 'POST'])
def cmd():
    if request.method == 'POST':
        command = request.form.get('command')
        log_request(request, f'Attempted command injection\nCommand: {command}', log_data=False)
        return "Command execution failed", 500
    log_request(request)
    return render_template('command_interface.html')

@app.route('/sql', methods=['GET', 'POST'])
def sql():
    if request.method == 'POST':
        query = request.form.get('query')
        log_request(request, f'Attempted SQL injection\nQuery: {query}', log_data=False)
        return "SQL query execution failed", 500
    log_request(request)
    return render_template('sql_interface.html')

@app.route('/password.py')
def download_password_py():
    log_request(request, 'Attempted to download password.py')
    return send_file('password.py', as_attachment=True)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    image_data = data.get('image')
    if image_data and image_data != "data:,":
        image_data = image_data.split(',')[1]
        image_data = base64.b64decode(image_data)
        filename = f'captured_image_{uuid.uuid4().hex}.png'
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        # Analyze the image for a face
        if not face_detected(image_data):
            return jsonify({"message": "No face detected. Please try again."}), 400
        
        log_request(request, f'Webcam verification image captured: {filename}', log_data=False)
        return jsonify({"message": "Verification successful"}), 200
    else:
        return jsonify({"message": "Verification failed"}), 400

@app.route('/email', methods=['POST'])
def email():
    data = request.json
    email = data.get('email')
    if email:
        log_request(request, f'Email submitted\nEmail: {email}', log_data=False)
        return jsonify({"message": "Email submitted"}), 200
    else:
        return jsonify({"message": "Failed to submit email"}), 400

def log_request(req, extra_info=None, log_data=True):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {req.remote_addr} {req.method} {req.path}\nHeaders: {req.headers}"
    if log_data and req.data:
        log_entry += "\nData: [Data not logged]"
    if extra_info:
        log_entry += f"\n{extra_info}"
    log_entry += "\n" + "-"*50
    app.logger.info(log_entry)

def get_ip_info(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        return response.json()
    except Exception as e:
        return f"Error fetching IP info: {e}"

def face_detected(image_data):
    # Load the image data into OpenCV
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Load OpenCV's pre-trained face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Return True if at least one face is detected, otherwise False
    return len(faces) > 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
