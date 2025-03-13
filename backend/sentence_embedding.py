import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import time
from nltk.corpus import stopwords
import nltk
from tqdm import tqdm
from typing import Optional, Dict

nltk.download('stopwords')

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36"
)

# List of domains to avoid scraping (from previous errors)
DO_NOT_SCRAPE_DOMAINS = {
    "azernews.az",
    "catchmyparty.com",
    "creekcountysheriff.com"
    "etsy.com",
    "facebook.com",
    "health.usnews.com",
    "heraldsun.com.au",
    "instagram.com",
    "news.com.au",
    "thecontactdetails.com",
    "tullahomanews.com",
    "usnews.com",
}

def should_skip_url(url):
    """Check if the URL's domain is in the do-not-scrape list."""
    for domain in DO_NOT_SCRAPE_DOMAINS:
        if domain in url:
            return True
    return False

def get_page_text(url):
    """
    Fetch the raw text from a webpage with custom headers and basic error handling.
    Returns a string of the webpage's visible text or None if it fails.
    """
    if should_skip_url(url):
        return None  # Skip this URL silently

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None  # Skip silently

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.extract()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else None

def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text.split()

def build_signature_from_topX(topX_urls, cache: Optional[Dict[str, str]] = None):
    """
    1. Fetch + tokenize text from each top-5 URL.
    2. Aggregate and find top frequent words.
    3. Return as a 'signature' dictionary or set of words.
    """
    all_words = []
    common_stopwords = set(stopwords.words('english'))
    additional_ignore = {"com", "www", "http", "https", "org", "bsky", "app", "profile"}
    common_stopwords.update(additional_ignore)

    for url in tqdm(topX_urls, desc="🏗️ Building signature"):
        page_text = get_page_text(url)
        if page_text:
            words = tokenize(page_text)
            all_words.extend(words)
            # Optional cache the page text
            if cache is not None:
                cache[url] = page_text
        # time.sleep(1)

    freq = Counter(w for w in all_words if w not in common_stopwords and len(w) > 2)
    return set(w for w, _ in freq.most_common(50))

def compute_signature_overlap(signature_set, text, threshold=5):
    words = tokenize(text)
    overlap = sum(1 for w in words if w in signature_set)
    return overlap >= threshold

if __name__ == "__main__":
    links_with_scores = []  # Populate this with (score, url) tuples

    links_with_scores.sort(key=lambda x: x[0], reverse=True)
    top5 = [x[1] for x in links_with_scores[:5]]
    the_rest = [x[1] for x in links_with_scores[5:]]

    signature = build_signature_from_topX(top5)
    yes_list, no_list = [], []

    for url in the_rest:
        page_text = get_page_text(url)
        if page_text:
            if compute_signature_overlap(signature, page_text):
                yes_list.append(url)
            else:
                no_list.append(url)
        time.sleep(1)

    print("\n=== Baseline (Top 5) ===")
    for link in top5:
        print("   ", link)
    print("\n=== Yes (Likely Same Person) ===")
    for link in yes_list:
        print("   ", link)
    print("\n=== No (Likely Different) ===")
    for link in no_list:
        print("   ", link)
