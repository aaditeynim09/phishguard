import pandas as pd
from urllib.parse import urlparse
import re
import socket
import ssl
import whois
from datetime import datetime
import requests

# Expanded suspicious keywords
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'bank', 'account', 'security', 'update', 'signin',
    'confirm', 'password', 'credential', 'wallet', 'payment', 'billing',
    'suspend', 'unusual', 'authorize', 'authenticate', 'recover'
]

# Top brands to check for impersonation (Levenshtein distance)
TOP_BRANDS = ['paypal', 'google', 'facebook', 'apple', 'amazon', 'netflix',
              'microsoft', 'instagram', 'twitter', 'linkedin', 'dropbox']

SUSPICIOUS_TLDS = ['.xyz', '.top', '.club', '.online', '.site', '.tk', '.ml', '.ga', '.cf']


# ─── Basic URL Features ────────────────────────────────────────────────────────

def get_url_length(url):
    return len(url)

def get_dot_count(url):
    return url.count('.')

def has_https(url):
    return 1 if urlparse(url).scheme == 'https' else 0

def has_suspicious_keywords(url):
    return 1 if any(k in url.lower() for k in SUSPICIOUS_KEYWORDS) else 0

def has_ip_address(url):
    domain = urlparse(url).netloc
    return 1 if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', domain) else 0

def get_symbol_count(url, symbol):
    return url.count(symbol)

def get_subdomain_depth(url):
    """Number of subdomains. google.com = 0, mail.google.com = 1"""
    netloc = urlparse(url).netloc.replace('www.', '')
    parts = netloc.split('.')
    return max(0, len(parts) - 2)

def get_path_depth(url):
    """Number of / in path"""
    return urlparse(url).path.count('/')

def has_suspicious_tld(url):
    netloc = urlparse(url).netloc.lower()
    return 1 if any(netloc.endswith(tld) for tld in SUSPICIOUS_TLDS) else 0

def has_redirect(url):
    """Checks if URL contains another URL inside it (redirect pattern)"""
    return 1 if url.count('http') > 1 else 0

def get_special_char_ratio(url):
    """Ratio of special characters to total URL length"""
    special = sum(1 for c in url if c in '!@#$%^&*()_+=[]{}|;:,<>?~`')
    return round(special / len(url), 4) if len(url) > 0 else 0

def levenshtein(s1, s2):
    """Basic Levenshtein distance"""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for c1 in s1:
        curr = [0] * (len(s2) + 1)
        curr[0] = prev[0] + 1
        for i, c2 in enumerate(s2):
            curr[i+1] = min(prev[i] + (c1 != c2), curr[i] + 1, prev[i+1] + 1)
        prev = curr
    return prev[len(s2)]

def get_brand_impersonation_score(url):
    """Checks if any top brand name appears in the URL but isn't the actual domain."""
    netloc = urlparse(url).netloc.lower().replace('www.', '')
    actual_domain = netloc.split('.')[0]
    
    for brand in TOP_BRANDS:
        # Brand appears somewhere in URL but domain isn't exactly the brand
        if brand in url.lower() and actual_domain != brand:
            return 1
    
    # Also check Levenshtein on actual domain
    distances = [levenshtein(actual_domain, brand) for brand in TOP_BRANDS]
    min_dist = min(distances)
    return 1 if 0 < min_dist <= 3 else 0


# ─── WHOIS Features ────────────────────────────────────────────────────────────

def get_domain_age_days(url):
    """Returns domain age in days. -1 if lookup fails."""
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            return (datetime.now() - creation_date).days
    except Exception:
        pass
    return -1

def get_domain_expiry_days(url):
    """Returns days until domain expires. -1 if lookup fails."""
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        w = whois.whois(domain)
        expiry_date = w.expiration_date
        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]
        if expiry_date:
            return (expiry_date - datetime.now()).days
    except Exception:
        pass
    return -1


# ─── SSL Features ──────────────────────────────────────────────────────────────

def has_valid_ssl(url):
    """Returns 1 if SSL cert is valid, 0 otherwise."""
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain, 443))
            return 1
    except Exception:
        return 0


# ─── Master Function ───────────────────────────────────────────────────────────

def extract_features(url, use_whois=True, use_ssl=True):
    """
    Extracts all features from a URL.
    Set use_whois=False and use_ssl=False for fast/offline mode.
    """
    features = {
        # Basic
        'url_length': get_url_length(url),
        'dot_count': get_dot_count(url),
        'has_https': has_https(url),
        'has_suspicious_keywords': has_suspicious_keywords(url),
        'has_ip_address': has_ip_address(url),
        'at_symbol_count': get_symbol_count(url, '@'),
        'hyphen_count': get_symbol_count(url, '-'),
        'double_slash_count': get_symbol_count(url, '//'),

        # Structural
        'subdomain_depth': get_subdomain_depth(url),
        'path_depth': get_path_depth(url),
        'has_suspicious_tld': has_suspicious_tld(url),
        'has_redirect': has_redirect(url),
        'special_char_ratio': get_special_char_ratio(url),
        'brand_impersonation': get_brand_impersonation_score(url),

        # WHOIS (slow — disable for inference speed)
        'domain_age_days': get_domain_age_days(url) if use_whois else -1,
        'domain_expiry_days': get_domain_expiry_days(url) if use_whois else -1,

        # SSL
        'has_valid_ssl': has_valid_ssl(url) if use_ssl else -1,
    }
    return features


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        urls_df = pd.read_csv('../data/urls_balanced.csv')
    except FileNotFoundError:
        print("Error: 'data/urls.csv' not found.")
        exit()

    print(f"Loaded {len(urls_df)} URLs.")
    print("Note: WHOIS lookups are slow (~1-2s per URL). For large datasets, set use_whois=False first.\n")

    features_list = []
    for index, row in urls_df.iterrows():
        url = row['url']
        label = row['label']

        try:
            url_features = extract_features(url, use_whois=False, use_ssl=False)

        except Exception as e:
            print(f"Error on URL {url}: {e}")
            continue

        url_features['label'] = int(label)
        features_list.append(url_features)

        if (index + 1) % 50 == 0:
            print(f"Processed {index + 1}/{len(urls_df)} URLs...")

    features_df = pd.DataFrame(features_list)
    output_path = '../data/features.csv'
    features_df.to_csv(output_path, index=False)

    print(f"\nDone. {len(features_df)} records saved to '{output_path}'.")
    print(features_df.head())