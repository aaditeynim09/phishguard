🛡️ PhishGuard
Machine-Learning Powered Phishing URL Detector + Chrome Extension
PhishGuard is a cybersecurity tool that analyzes website URLs in real-time and predicts whether they are legitimate or phishing using machine learning. It comes with a Chrome extension and a Cloud-deployed API, making it usable like a real security product.

🚀 Live API
🔗 https://phishguard-api-p12g.onrender.com
If you open the link directly, you’ll see:
Method Not Allowed — that’s normal. The API only accepts POST requests.

📌 Features
✔ Detects suspicious and phishing URLs using ML
✔ Chrome extension for real-time scanning
✔ Trained on real phishing datasets + expanded samples
✔ REST API powered by Flask + Gunicorn
✔ Fully deployed online via Render
✔ Lightweight, fast, and beginner-friendly architecture

🧠 How It Works
The Chrome extension captures the current tab URL
The URL is sent to the deployed public API
The backend extracts features (keywords, URL structure, HTTPS usage, etc.)
The trained ML model classifies the URL
The extension displays a SAFE / WARNING / PHISHING status

🖼️ Screenshot
(Optional — Add after testing)

📁 Project Structure
phishguard/
│
├── data/               # Dataset (URL list)
├── models/             # Trained ML models
├── src/                # Backend code (Flask + training scripts)
│   ├── extract_features.py
│   ├── train_model.py
│   └── api.py
│
├── extension/          # Chrome extension source
│   ├── popup.html
│   ├── popup.js
│   └── manifest.json
│
└── requirements.txt


🔧 Installation (Local)
1️⃣ Clone Repository
git clone https://github.com/aaditeynim09/phishguard
cd phishguard

2️⃣ Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate   # Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Train Model (Optional if model already included)
cd src
python extract_features.py
python train_model.py

5️⃣ Run API Locally
python api.py

API will run at: http://127.0.0.1:5000

🧩 Chrome Extension Setup
Go to: chrome://extensions/
Enable Developer Mode
Click Load unpacked
Select the extension/ folder
Pin 📌 the extension for easy access

🌍 Deployment (Render)
Backend is deployed using:
Build Command: pip install -r requirements.txt
Start Command: gunicorn --chdir src api:app

After updating the model:
python src/train_model.py

Commit & push changes → Render redeploys automatically.

🧪 Sample API Request
curl -X POST -H "Content-Type: application/json" \
-d "{\"url\": \"http://paypal-login-security-check.xyz\"}" \
https://phishguard-api-p12g.onrender.com/predict

Example Response:
{
  "prediction": "phishing",
  "risk_score": 0.93,
  "url": "http://paypal-login-security-check.xyz"
}


🛠️ Tech Stack
ComponentTechnology
Language
Python
ML Model
Random Forest
Backend
Flask + Gunicorn
Frontend
Chrome Extension (HTML/CSS/JS)
Hosting
Render
Libraries
pandas, scikit-learn, joblib, requests

🔥 Future Improvements
Add WHOIS domain age scoring
SSL certificate inspection
AI-powered text content analysis
Dynamic alerting + reporting dashboard
Browser notifications + auto blocking

👨‍💻 Author
Aaditey Nim
📫 Feel free to fork, open issues, or contribute!

📜 License
MIT License — free to use, modify, and improve.
