import os
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from huggingface_hub import hf_hub_download

app = Flask(__name__)
CORS(app) # Allow all origins for simpler development with React

# Configure Database - Replace with your actual PostgreSQL credentials if different
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:Rs%40181075@localhost/lesion_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

# Load your model
model_path = hf_hub_download(
    repo_id="navinroshan09/lesion_skin_disease_detection",
    filename="skin_lesion_model.h5"
)

model = load_model(model_path)

# Ensure static folder exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    new_user = User(name=name,email=email, password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Using a very basic success response. A full professional app might use JWTs here.
        return jsonify({
            'message': 'Logged in successfully', 
            'user': {'id': user.id, 'email': user.email}
        }), 200
        
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load and preprocess the image
    img = image.load_img(filepath, target_size=(224, 224))  # Adjust size to match model
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)[0]
    confidence = float(np.max(prediction)) * 100
    result = 'Malignant' if np.argmax(prediction) == 1 else 'Benign'

    return jsonify({
        'result': result,
        'confidence': round(confidence, 2),
        'image_url': f'/{filepath}'
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)