# import os
# import uuid
# import numpy as np
# from flask import Flask, render_template, request, jsonify, send_from_directory
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_cors import CORS
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# from huggingface_hub import hf_hub_download

# app = Flask(__name__)
# CORS(app)

# # -------------------- DATABASE CONFIG (FIXED) --------------------
# database_url = os.getenv('DATABASE_URL')

# if database_url and database_url.startswith("postgres://"):
#     database_url = database_url.replace("postgres://", "postgresql://", 1)

# app.config['SQLALCHEMY_DATABASE_URI'] = database_url
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # -------------------- USER MODEL --------------------
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(256), nullable=False)

# with app.app_context():
#     db.create_all()

# # -------------------- MODEL LOADING (SAFE) --------------------
# model = None

# def load_my_model():
#     global model
#     if model is None:
#         hf_token = os.getenv("HF_TOKEN")
#         if hf_token:
#             from huggingface_hub import login
#             login(hf_token)

#         model_path = hf_hub_download(
#             repo_id="navinroshan09/lesion_skin_disease_detection",
#             filename="skin_lesion_model.h5"
#         )
#         model = load_model(model_path, compile=False)

# # -------------------- UPLOAD FOLDER --------------------
# UPLOAD_FOLDER = 'static/uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # -------------------- REGISTER --------------------
# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#     password = data.get('password')
    
#     if not name or not email or not password:
#         return jsonify({'error': 'name , email and password are required'}), 400
        
#     if User.query.filter_by(email=email).first():
#         return jsonify({'error': 'email already exists'}), 400
        
#     hashed_password = generate_password_hash(password)
#     new_user = User(name=name, email=email, password_hash=hashed_password)
    
#     try:
#         db.session.add(new_user)
#         db.session.commit()
#         return jsonify({'message': 'User registered successfully'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': 'Failed to register'}), 500

# # -------------------- LOGIN --------------------
# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
    
#     user = User.query.filter_by(email=email).first()
    
#     if user and check_password_hash(user.password_hash, password):
#         return jsonify({
#             'message': 'Logged in successfully', 
#             'user': {'id': user.id, 'email': user.email}
#         }), 200
        
#     return jsonify({'error': 'Invalid email or password'}), 401

# # -------------------- PREDICT --------------------
# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         print("🚀 Predict API called")

#         try:
#             load_my_model()
#             print("Model loaded")
#         except Exception as e:
#             print("Model loading failed:", str(e))
#             return jsonify({
#                 'error': 'Failed to load model',
#                 'details': str(e)
#             }), 500
#         print("✅ Model loaded")

#         if model is None:
#             return jsonify({'error': 'Model not loaded'}), 500

#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['file']
#         print("📂 File received:", file.filename)

#         filename = str(uuid.uuid4()) + "_" + file.filename
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         print("🖼 Image saved at:", filepath)

#         img = image.load_img(filepath, target_size=(224, 224))
#         img_array = image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0) / 255.0

#         print("🤖 Running prediction...")

#         prediction = model.predict(img_array)[0]

#         confidence = float(np.max(prediction)) * 100
#         result = 'Malignant' if np.argmax(prediction) == 1 else 'Benign'

#         print("✅ Prediction done")

#         return jsonify({
#             'result': result,
#             'confidence': round(confidence, 2)
#         })

#     except Exception as e:
#         print("❌ ERROR:", str(e))
#         return jsonify({'error': str(e)}), 500

# # -------------------- HEALTH CHECK --------------------
# @app.route('/health', methods=['GET', 'POST'])

# def health():
#     return jsonify({
#         "status": "ok",
#         "message": "API is running",
#         "model_loaded": model is not None
#     }), 200

# # -------------------- RUN SERVER --------------------
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # suppress TF logs

import uuid
import numpy as np
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from huggingface_hub import hf_hub_download, login

app = Flask(__name__)
CORS(app)

# -------------------- DATABASE CONFIG --------------------
database_url = os.getenv('DATABASE_URL')

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- USER MODEL --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# ✅ FIX: Delay DB creation (IMPORTANT)
with app.app_context():
    db.create_all()

# -------------------- MODEL LOADING --------------------
model = None

def load_my_model():
    global model
    if model is None:
        print("⬇️ Loading model from Hugging Face...")

        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            login(hf_token)

        model_path = hf_hub_download(
            repo_id="navinroshan09/lesion_skin_disease_detection",
            filename="skin_lesion_model.h5"
        )

        model = load_model(model_path, compile=False)
        print("✅ Model loaded successfully")

# -------------------- UPLOAD FOLDER --------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- REGISTER --------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'name , email and password are required'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already exists'}), 400
        
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to register'}), 500

# -------------------- LOGIN --------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            'message': 'Logged in successfully', 
            'user': {'id': user.id, 'email': user.email}
        }), 200
        
    return jsonify({'error': 'Invalid email or password'}), 401

# -------------------- PREDICT --------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("🚀 Predict API called")

        load_my_model()

        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        print("📂 File received:", file.filename)

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type. Only png, jpg, and jpeg are allowed'
            }), 400

        filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        print("🤖 Running prediction...")

        prediction = model.predict(img_array)[0]

        confidence = float(np.max(prediction)) * 100
        result = 'Malignant' if np.argmax(prediction) == 1 else 'Benign'

        print("✅ Prediction done")

        return jsonify({
            'result': result,
            'confidence': round(confidence, 2)
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'error': str(e)}), 500

# -------------------- HEALTH CHECK --------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running",
        "model_loaded": model is not None
    }), 200

# -------------------- RUN SERVER --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
