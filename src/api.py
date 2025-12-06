from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

# Import the feature extraction function from extract_features.py
from extract_features import extract_features

# --- Load Model and Feature Names ---
# Construct absolute paths to ensure the model loads correctly on the server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'phishguard_model.joblib')
FEATURES_PATH = os.path.join(BASE_DIR, '..', 'models', 'feature_names.joblib')

try:
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURES_PATH)
    print("Model and feature names loaded successfully.")
except FileNotFoundError:
    print("Error: Model or feature names not found. Train the model first.")
    exit()

# --- Initialize Flask App ---
app = Flask(__name__)

# --- API Endpoint for Prediction ---
@app.route('/predict', methods=['POST'])
def predict():
    """Receives a URL, extracts features, and returns a phishing prediction."""
    data = request.get_json()

    # Validate input
    if not data or 'url' not in data or not data['url']:
        return jsonify({'error': 'Invalid input: URL is required.'}), 400

    url = data['url']

    try:
        # 1. Extract features from the URL
        url_features_dict = extract_features(url)
        
        # 2. Convert features to a DataFrame in the correct order
        # The model expects a 2D array, so we create a DataFrame and then get values
        features_df = pd.DataFrame([url_features_dict], columns=feature_names)

        # 3. Make a prediction
        prediction_proba = model.predict_proba(features_df)[0]
        prediction = model.predict(features_df)[0]

        risk_score = float(prediction_proba[1])  # Probability of being phishing
        prediction_label = 'phishing' if prediction == 1 else 'legit'

        # 4. Prepare the response
        response = {
            'url': url,
            'prediction': prediction_label,
            'risk_score': round(risk_score, 4),
            'features_used': url_features_dict
        }
        
        return jsonify(response)

    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return jsonify({'error': 'Failed to process the URL.'}), 500

# --- Run the Flask App ---
if __name__ == '__main__':
    # Running on 0.0.0.0 makes it accessible from the network
    # Useful for testing the Chrome extension
    app.run(host='0.0.0.0', port=5000, debug=True)
