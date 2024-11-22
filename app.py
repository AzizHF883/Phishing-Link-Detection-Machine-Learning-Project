import pandas as pd
import pickle
import os
import re
import time
import requests
import random
import tldextract
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# Headers to simulate browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
}

# Load brand names and shortening services
brands = pd.read_csv('brand.csv')['brand'].str.lower().tolist()
shortening_services = [
    "bit.ly", "goo.gl", "t.co", "tinyurl.com", "is.gd",
    "buff.ly", "ow.ly", "rebrand.ly", "bl.ink", "shorte.st"
]


# Helper: Calculate word stats
def word_stats(text):
    words = text.split('.')
    return {
        'shortest': min(len(w) for w in words) if words else 0,
        'longest': max(len(w) for w in words) if words else 0,
        'average': sum(len(w) for w in words) / len(words) if words else 0
    }


# WHOIS scraping function
def extract_whois_info(url, delay=1, retries=3):
    domain = tldextract.extract(url).registered_domain
    if not domain:
        return 0, -1, -1  # WHOIS domain not found

    whois_url = f"https://www.whois.com/whois/{domain}"
    for attempt in range(retries):
        try:
            response = requests.get(whois_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            registered_on = soup.find('div', string='Registered On:').find_next_sibling('div').get_text(strip=True)
            expires_on = soup.find('div', string='Expires On:').find_next_sibling('div').get_text(strip=True)

            reg_date = pd.to_datetime(registered_on, errors='coerce')
            exp_date = pd.to_datetime(expires_on, errors='coerce')

            domain_age = (pd.Timestamp.now() - reg_date).days if not pd.isna(reg_date) else -1
            reg_length = (exp_date - reg_date).days if not pd.isna(exp_date) and not pd.isna(reg_date) else -1

            time.sleep(delay)
            return 1, domain_age, reg_length  # Success
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {domain}: {e}")
            time.sleep(2)

    return 0, -1, -1  # WHOIS failed after retries


def is_external_favicon(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        icon = soup.find('link', rel='icon')
        if icon and 'href' in icon.attrs:
            icon_url = icon['href']
            if not icon_url.startswith(('http', 'https')):
                icon_url = urlparse(url).scheme + '://' + urlparse(url).netloc + icon_url
            return 1 if urlparse(icon_url).netloc != urlparse(url).netloc else 0
        return 0
    except:
        return 0


# Feature extraction function
def extract_features(url):
    parsed_url = urlparse(url)
    ext = tldextract.extract(url)

    # URL-based Features
    features = {
        'URL': url,
        'Length of URL': len(url),
        'Length of Hostname': len(parsed_url.netloc),
        'IP Address': 1 if re.match(r'\d+\.\d+\.\d+\.\d+', parsed_url.netloc) else 0,
        'Number of Dots': url.count('.'),
        'Number of Hyphens': url.count('-'),
        'Number of @ Symbols': url.count('@'),
        'Number of Question Marks': url.count('?'),
        'Number of & Symbols': url.count('&'),
        'Number of OR Keywords': url.lower().count(' or '),
        'Number of = Symbols': url.count('='),
        'Number of Underscores': url.count('_'),
        'Number of Tildes': url.count('~'),
        'Number of Percent Signs': url.count('%'),
        'Number of Slashes': url.count('/'),
        'Number of Asterisks': url.count('*'),
        'Number of Colons': url.count(':'),
        'Number of Commas': url.count(','),
        'Number of Semicolons': url.count(';'),
        'Number of Dollar Signs': url.count('$'),
        'Number of Spaces': url.count(' '),
        'Number of www': url.lower().count('www'),
        'Number of .com': url.lower().count('.com'),
        'Number of Double Slashes': url.count('//'),
        'HTTP in Path': 1 if 'http' in parsed_url.path.lower() else 0,
        'HTTPS Token': 1 if 'https' in url.lower() else 0,
        'Ratio of Digits in URL': sum(c.isdigit() for c in url) / len(url),
        'Ratio of Digits in Hostname': sum(c.isdigit() for c in parsed_url.netloc) / len(parsed_url.netloc),
        'Punycode': 1 if 'xn--' in url else 0,
        'Port': 1 if ':' in parsed_url.netloc and not parsed_url.netloc.endswith(':80') else 0,
        'TLD in Path': 1 if ext.suffix in parsed_url.path else 0,
        'TLD in Subdomain': 1 if ext.suffix in ext.subdomain else 0,
        'Abnormal Subdomain': 1 if len(ext.subdomain.split('.')) > 2 else 0,
        'Number of Subdomains': len(ext.subdomain.split('.')),
        'Prefix-Suffix': 1 if '-' in parsed_url.netloc else 0,
        'Domain in Brand': 1 if ext.domain in brands else 0,
        'Brand in Subdomain': 1 if any(b in ext.subdomain for b in brands) else 0,
        'Brand in Path': 1 if any(b in parsed_url.path for b in brands) else 0,
    }

    # WHOIS and favicon features
    registered, age, reg_length = extract_whois_info(url)
    features.update({
        'WHOIS Registered Domain': registered,
        'Domain Age': age,
        'Domain Registration Length': reg_length,
        'External Favicon': is_external_favicon(url),
        'Shortening Service': 1 if ext.domain in shortening_services else 0
    })

    # Word stats
    host_stats = word_stats(ext.domain)
    path_stats = word_stats(parsed_url.path)

    features.update({
        'Shortest Word in Host': host_stats['shortest'],
        'Longest Word in Host': host_stats['longest'],
        'Average Word in Host': host_stats['average'],
        'Shortest Word in Path': path_stats['shortest'],
        'Longest Word in Path': path_stats['longest'],
        'Average Word in Path': path_stats['average']
    })

    return features


# Load models function
def load_models():
    model_files = [
        "Random_Forest_model.pkl",
        "Gradient_Boosting_model.pkl",
        "XGBoost_model.pkl",
        "AdaBoost_model.pkl",
        "Decision_Tree_model.pkl"
    ]
    models = {}
    for model_file in model_files:
        with open(model_file, "rb") as file:
            model_name = model_file.split("_model.pkl")[0].replace("_", " ")
            models[model_name] = pickle.load(file)
    return models


# Main function
def main():
    url = input("Enter the URL: ")  # For Colab environment

    # Feature extraction
    features = extract_features(url)
    feature_df = pd.DataFrame([features])
    # print("\nExtracted Features:")
    # print(feature_df)

    # Load trained models
    print("\nLoading Models...")
    models = load_models()
    phish_count = 0

    # Prediction
    print("\nPrediction Results:")
    for name, model in models.items():
        prediction = model.predict(feature_df.drop(columns=['URL']))[0]
        result = "Phishing" if prediction == 1 else "General URL"
        if result == "Phishing": phish_count += 1
        print(f"{name}: {result}")
    print(f"\nPhishing Score: {phish_count} out of 5")


if __name__ == "__main__":
    main()
