# 🛡️ PhishGuard — Machine Learning Phishing URL Detector

PhishGuard is a cybersecurity project that uses machine learning to detect phishing websites in real-time. It includes a data processing pipeline, a Flask API for predictions, and a Chrome extension to warn users about suspicious URLs.

## ✨ Features

- **Feature Extraction**: Analyzes URLs based on length, symbols, keywords, and more.
- **ML Model**: A `RandomForestClassifier` trained to distinguish between phishing and legitimate URLs.
- **Real-Time API**: A Flask server that provides instant predictions for any given URL.
- **Chrome Extension**: A simple browser extension that scans the current page and displays a safety rating.

## 🏗️ Architecture

The project is structured into three main components:

1.  **Data Pipeline**: `extract_features.py` processes a list of URLs (`data/urls.csv`) and converts them into a set of numerical features (`data/features.csv`).
2.  **ML Model Training**: `train_model.py` uses the extracted features to train a classifier and saves the model (`models/phishguard_model.joblib`).
3.  **API & Extension**:
    - The **Flask API** (`src/api.py`) loads the trained model and exposes a `/predict` endpoint.
    - The **Chrome Extension** (`extension/`) sends the current tab's URL to the API and displays the result.

```
+-----------------------+      +---------------------+      +-----------------+
|   Chrome Extension    |----->|      Flask API      |----->|   ML Model      |
| (popup.js)            |      | (api.py)            |      | (.joblib)       |
+-----------------------+      +---------------------+      +-----------------+
```

## 🚀 Setup and Installation

Follow these steps to get the project running locally.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd phishguard
```

### 2. Set Up the Python Environment

Create a virtual environment and install the required packages.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Features and Train the Model

Run the following scripts from the `src` directory:

```bash
cd src

# 1. Extract features from the URL dataset
python extract_features.py

# 2. Train the machine learning model
python train_model.py
```

### 4. Run the Flask API Server

Start the Flask API to handle prediction requests.

```bash
python api.py
```

The server will start on `http://127.0.0.1:5000`.

### 5. Install the Chrome Extension

1.  Open Chrome and navigate to `chrome://extensions`.
2.  Enable **Developer mode** using the toggle in the top-right corner.
3.  Click the **Load unpacked** button.
4.  Select the `phishguard/extension` directory from the project folder.
5.  The PhishGuard extension icon (🛡️) will appear in your browser toolbar.

## ☁️ Deployment to Render

To make the API publicly accessible, you can deploy it as a web service on Render.

### 1. Push to GitHub

First, make sure your project is a Git repository and push it to GitHub. The `.gitignore` file is already configured to include the necessary model files for deployment.

### 2. Create a New Web Service on Render

1.  Go to the [Render Dashboard](https://dashboard.render.com/) and click **New +** > **Web Service**.
2.  Connect your GitHub account and select your `phishguard` repository.
3.  Configure the service with the following settings:
    - **Name**: `phishguard-api` (or your preferred name).
    - **Root Directory**: Leave this blank.
    - **Environment**: `Python 3`.
    - **Region**: Choose a region close to you.
    - **Build Command**: `pip install -r requirements.txt`.
    - **Start Command**: `gunicorn --chdir src api:app`.

4.  Click **Create Web Service**. Render will automatically build and deploy your API.

### 3. Update the Chrome Extension

Once deployed, Render will provide you with a public URL (e.g., `https://phishguard-api.onrender.com`).

1.  Open `extension/popup.js` in your code editor.
2.  Change the `API_ENDPOINT` to your new Render URL:

    ```javascript
    const API_ENDPOINT = 'https://phishguard-api.onrender.com/predict';
    ```

3.  Go to `chrome://extensions`, click **Reload** on the PhishGuard extension, and you're all set!

## 🧪 Example Prediction

To test the API directly, you can use a tool like `curl`:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"url": "http://example-login-security.com"}' \
     http://127.0.0.1:5000/predict
```

**Expected Response:**

```json
{
  "prediction": "phishing",
  "risk_score": 0.9876,
  "url": "http://example-login-security.com",
  "features_used": { ... }
}
```

## 🔮 Future Improvements

This project is a great starting point. Here are some ways it could be improved:

- **Expand the Dataset**: Collect more diverse and recent phishing URLs to improve model accuracy.
- **Advanced Features**: Implement `WHOIS` lookups for domain age and `SSL` certificate validation.
- **Better Models**: Experiment with more powerful classifiers like `XGBoost` or `LightGBM`.
- **Deployment**: Deploy the Flask API to a cloud service like Heroku or Render for public access.
- **CI/CD Pipeline**: Automate testing and deployment using GitHub Actions.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
