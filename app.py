import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

# Load your model
model = load_model(r"C:\Users\NAVIN ROSHAN S\OneDrive\Desktop\mini project 3rd year\skin_lesion_model.h5")

# Ensure static folder exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

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
    app.run(debug=True)
