document.addEventListener('DOMContentLoaded', () => {
    const scanButton = document.getElementById('scan-btn');
    const resultDiv = document.getElementById('result');
    const predictionText = document.getElementById('prediction-text');
    const riskScoreText = document.getElementById('risk-score-text');
    const triggersDiv = document.getElementById('triggers');
    const triggersList = document.getElementById('triggers-list');
    const historyList = document.getElementById('history-list');
    const loader = document.getElementById('loader');

    const API_ENDPOINT = 'https://phishguard-api-p12g.onrender.com/predict';

    // Load history on popup open
    loadHistory();

    scanButton.addEventListener('click', () => {
        scanButton.disabled = true;
        loader.style.display = 'block';
        resultDiv.style.display = 'none';
        triggersDiv.style.display = 'none';

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            if (!currentTab || !currentTab.url) {
                displayError('Could not get URL of the current tab.');
                return;
            }

            const urlToScan = currentTab.url;

            fetch(API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlToScan }),
            })
            .then(response => {
                if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
                return response.json();
            })
            .then(data => {
                displayResult(data);
                saveToHistory(data);
                loadHistory();
            })
            .catch(error => {
                console.error('Error:', error);
                displayError('Failed to connect to the prediction server.');
            })
            .finally(() => {
                scanButton.disabled = false;
                loader.style.display = 'none';
            });
        });
    });

    function displayResult(data) {
        const { prediction, risk_score, triggers } = data;

        riskScoreText.textContent = `Risk Score: ${(risk_score * 100).toFixed(2)}%`;
        resultDiv.className = 'result-area';

        if (prediction === 'PHISHING') {
            predictionText.textContent = '🟥 PHISHING';
            resultDiv.classList.add('high-risk');
        } else if (prediction === 'SUSPICIOUS') {
            predictionText.textContent = '🟨 SUSPICIOUS';
            resultDiv.classList.add('suspicious');
        } else {
            predictionText.textContent = '🟩 SAFE';
            resultDiv.classList.add('safe');
        }

        resultDiv.style.display = 'block';

        // Show triggers if any
        if (triggers && triggers.length > 0) {
            triggersList.innerHTML = '';
            triggers.forEach(trigger => {
                const li = document.createElement('li');
                li.textContent = trigger;
                triggersList.appendChild(li);
            });
            triggersDiv.style.display = 'block';
        }
    }

    function displayError(message) {
        predictionText.textContent = message;
        riskScoreText.textContent = 'Ensure the server is running.';
        resultDiv.className = 'result-area high-risk';
        resultDiv.style.display = 'block';
    }

    function saveToHistory(data) {
        chrome.storage.local.get({ history: [] }, (result) => {
            const history = result.history;
            history.unshift({
                url: data.url,
                prediction: data.prediction,
                risk_score: data.risk_score,
                time: new Date().toLocaleTimeString()
            });
            // Keep only last 10
            if (history.length > 10) history.pop();
            chrome.storage.local.set({ history });
        });
    }

    function loadHistory() {
        chrome.storage.local.get({ history: [] }, (result) => {
            historyList.innerHTML = '';
            if (result.history.length === 0) {
                historyList.innerHTML = '<li style="color:#888">No scans yet.</li>';
                return;
            }
            result.history.forEach(item => {
                const li = document.createElement('li');
                const emoji = item.prediction === 'PHISHING' ? '🟥' :
                              item.prediction === 'SUSPICIOUS' ? '🟨' : '🟩';
                const shortUrl = item.url.length > 30 ? item.url.substring(0, 30) + '...' : item.url;
                li.textContent = `${emoji} ${shortUrl} (${item.time})`;
                li.title = item.url;
                historyList.appendChild(li);
            });
        });
    }
});