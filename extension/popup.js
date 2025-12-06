document.addEventListener('DOMContentLoaded', () => {
    const scanButton = document.getElementById('scan-btn');
    const resultDiv = document.getElementById('result');
    const predictionText = document.getElementById('prediction-text');
    const riskScoreText = document.getElementById('risk-score-text');
    const loader = document.getElementById('loader');

    // API endpoint for the local Flask server
    const API_ENDPOINT = 'https://phishguard-api-p12g.onrender.com';

    scanButton.addEventListener('click', () => {
        // Disable button and show loader
        scanButton.disabled = true;
        loader.style.display = 'block';
        resultDiv.style.display = 'none';

        // Get the URL of the current active tab
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            if (!currentTab || !currentTab.url) {
                displayError('Could not get URL of the current tab.');
                return;
            }

            const urlToScan = currentTab.url;

            // Make a POST request to the Flask API
            fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: urlToScan }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API Error: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                displayResult(data);
            })
            .catch(error => {
                console.error('Error:', error);
                displayError('Failed to connect to the prediction server.');
            })
            .finally(() => {
                // Re-enable button and hide loader
                scanButton.disabled = false;
                loader.style.display = 'none';
            });
        });
    });

    function displayResult(data) {
        const { prediction, risk_score } = data;

        // Update text content
        riskScoreText.textContent = `Risk Score: ${(risk_score * 100).toFixed(2)}%`;

        // Reset classes and set new one based on risk
        resultDiv.className = 'result-area'; // Reset
        if (risk_score > 0.75) {
            predictionText.textContent = '🟥 High Risk';
            resultDiv.classList.add('high-risk');
        } else if (risk_score > 0.4) {
            predictionText.textContent = '🟨 Suspicious';
            resultDiv.classList.add('suspicious');
        } else {
            predictionText.textContent = '🟩 Safe';
            resultDiv.classList.add('safe');
        }

        resultDiv.style.display = 'block';
    }

    function displayError(message) {
        predictionText.textContent = message;
        riskScoreText.textContent = 'Please ensure the local server is running.';
        resultDiv.className = 'result-area high-risk'; // Use red for errors
        resultDiv.style.display = 'block';
    }
});
