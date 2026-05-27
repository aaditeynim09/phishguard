from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
import numpy as np
from extract_features import extract_features

# --- Load Model and Feature Names ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'phishguard_model.joblib')
FEATURES_PATH = os.path.join(BASE_DIR, '..', 'models', 'feature_names.joblib')

try:
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURES_PATH)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model not found. Train the model first.")
    exit()

app = Flask(__name__)

# Simple in-memory cache {url: response}
_cache = {}

def get_triggers(features: dict) -> list:
    """Returns human-readable reasons why a URL was flagged."""
    triggers = []

    if features.get('has_ip_address'):
        triggers.append("IP address used instead of domain name")
    if features.get('has_suspicious_keywords'):
        triggers.append("Contains suspicious keywords (login, verify, bank, etc.)")
    if features.get('brand_impersonation'):
        triggers.append("Domain looks like a brand impersonation")
    if features.get('has_suspicious_tld'):
        triggers.append("Suspicious top-level domain (.xyz, .tk, .ml, etc.)")
    if features.get('hyphen_count', 0) > 3:
        triggers.append(f"Excessive hyphens in URL ({features['hyphen_count']})")
    if features.get('subdomain_depth', 0) > 2:
        triggers.append(f"Unusually deep subdomain structure ({features['subdomain_depth']} levels)")
    if features.get('url_length', 0) > 75:
        triggers.append(f"Abnormally long URL ({features['url_length']} characters)")
    if features.get('has_redirect'):
        triggers.append("URL contains a redirect to another URL")
    if features.get('at_symbol_count', 0) > 0:
        triggers.append("Contains @ symbol (browser ignores everything before it)")
    if features.get('double_slash_count', 0) > 1:
        triggers.append("Multiple double-slashes detected")
    if features.get('domain_age_days', -1) != -1 and features['domain_age_days'] < 30:
        triggers.append(f"Very new domain (only {features['domain_age_days']} days old)")
    if features.get('domain_expiry_days', -1) != -1 and features['domain_expiry_days'] < 60:
        triggers.append(f"Domain expiring soon ({features['domain_expiry_days']} days)")
    if features.get('has_valid_ssl') == 0 and features.get('has_https') == 0:
        triggers.append("No HTTPS and no valid SSL certificate")

    return triggers

def get_risk_level(risk_score: float) -> str:
    if risk_score >= 0.75:
        return "PHISHING"
    elif risk_score >= 0.45:
        return "SUSPICIOUS"
    else:
        return "SAFE"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'url' not in data or not data['url']:
        return jsonify({'error': 'Invalid input: URL is required.'}), 400

    url = data['url'].strip()

    # Check cache
    if url in _cache:
        return jsonify(_cache[url])

    try:
        # Extract features (fast mode — no WHOIS/SSL for speed)
        url_features_dict = extract_features(url, use_whois=False, use_ssl=False)

        # Fill -1s with median (same as training)
        features_df = pd.DataFrame([url_features_dict], columns=feature_names)
        features_df.replace(-1, np.nan, inplace=True)
        features_df.fillna(0, inplace=True)

        # Predict
        prediction_proba = model.predict_proba(features_df)[0]
        prediction = model.predict(features_df)[0]
        risk_score = float(prediction_proba[1])

        # Get triggers
        triggers = get_triggers(url_features_dict)

        # Build response
        response = {
            'url': url,
            'prediction': get_risk_level(risk_score),
            'risk_score': round(risk_score, 4),
            'triggers': triggers,
            'trigger_count': len(triggers),
            'features': url_features_dict
        }

        # Cache it
        _cache[url] = response

        return jsonify(response)

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'Failed to process the URL.'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'phishguard', 'cached_urls': len(_cache)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)