import pandas as pd
from urllib.parse import urlparse
import re

# List of suspicious keywords to check for in the URL
SUSPICIOUS_KEYWORDS = ['login', 'verify', 'bank', 'account', 'security', 'update', 'signin']

def get_url_length(url):
    """Returns the length of the URL."""
    return len(url)

def get_dot_count(url):
    """Returns the number of dots in the URL."""
    return url.count('.')

def has_https(url):
    """Checks if the URL uses HTTPS. Returns 1 if true, 0 otherwise."""
    return 1 if urlparse(url).scheme == 'https' else 0

def has_suspicious_keywords(url):
    """Checks for the presence of suspicious keywords. Returns 1 if found, 0 otherwise."""
    return 1 if any(keyword in url.lower() for keyword in SUSPICIOUS_KEYWORDS) else 0

def has_ip_address(url):
    """Checks if the domain in the URL is an IP address. Returns 1 if true, 0 otherwise."""
    domain = urlparse(url).netloc
    # Simple regex to check for an IP address format
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    return 1 if ip_pattern.match(domain) else 0

def get_symbol_count(url, symbol):
    """Counts the occurrences of a specific symbol in the URL."""
    return url.count(symbol)

def extract_features(url):
    """Extracts all defined features from a given URL and returns them as a dictionary."""
    features = {
        'url_length': get_url_length(url),
        'dot_count': get_dot_count(url),
        'has_https': has_https(url),
        'has_suspicious_keywords': has_suspicious_keywords(url),
        'has_ip_address': has_ip_address(url),
        'at_symbol_count': get_symbol_count(url, '@'),
        'hyphen_count': get_symbol_count(url, '-'),
        'double_slash_count': get_symbol_count(url, '//'),
    }
    return features

if __name__ == '__main__':
    # Load the dataset of URLs
    try:
        urls_df = pd.read_csv('../data/urls.csv')
    except FileNotFoundError:
        print("Error: 'data/urls.csv' not found. Make sure the file exists.")
        exit()

    print(f"Loaded {len(urls_df)} URLs from 'data/urls.csv'.")

    # Extract features for each URL
    features_list = []
    for index, row in urls_df.iterrows():
        url = row['url']
        label = row['label']
        
        url_features = extract_features(url)
        url_features['label'] = 1 if label == 'phishing' else 0 # Convert label to binary
        features_list.append(url_features)
        
        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1}/{len(urls_df)} URLs...")

    # Create a DataFrame from the list of features
    features_df = pd.DataFrame(features_list)

    # Save the features to a new CSV file
    output_path = '../data/features.csv'
    features_df.to_csv(output_path, index=False)

    print(f"\nFeature extraction complete. {len(features_df)} records saved to '{output_path}'.")
    print("\nFirst 5 rows of the features dataset:")
    print(features_df.head())
