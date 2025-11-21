# utils.py
import requests
from bs4 import BeautifulSoup
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set a User-Agent to mimic a browser
REQUESTS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
REQUESTS_TIMEOUT = 15 # seconds

def fetch_website_content(url):
    """Fetches and parses basic content from a website URL."""
    if not url or not url.startswith(('http://', 'https://')):
        logging.warning(f"Invalid or missing URL: {url}")
        return None, None, None, None # Return None for all expected values

    # Prepend https:// if scheme is missing (common issue)
    if not url.startswith('http'):
        url = 'https://' + url

    logging.info(f"Fetching content from: {url}")
    content = None
    title = None
    meta_description = None
    body_text_snippet = None

    try:
        # Add a small delay before fetching
        time.sleep(1)
        response = requests.get(url, headers=REQUESTS_HEADERS, timeout=REQUESTS_TIMEOUT, allow_redirects=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Try to detect encoding, default to utf-8
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
        content = response.text

        soup = BeautifulSoup(content, 'lxml') # Use lxml parser

        # Extract Title
        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag else "No Title Found"

        # Extract Meta Description
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag and 'content' in meta_desc_tag.attrs:
            meta_description = meta_desc_tag['content'].strip()
        else:
             # Try property="og:description" as a fallback
            meta_og_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            if meta_og_desc_tag and 'content' in meta_og_desc_tag.attrs:
                 meta_description = meta_og_desc_tag['content'].strip()
            else:
                meta_description = "No Meta Description Found"


        # Extract a snippet of body text (limit length)
        body = soup.find('body')
        if body:
            all_text = body.get_text(separator=' ', strip=True)
            body_text_snippet = ' '.join(all_text.split())[:1000] # Limit to first 1000 chars
        else:
            body_text_snippet = "Could not extract body text."


        logging.info(f"Successfully fetched content for: {url}")
        return content, title, meta_description, body_text_snippet

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error fetching {url}")
    except requests.exceptions.TooManyRedirects:
        logging.error(f"Too many redirects for {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
    except Exception as e:
        logging.error(f"Error parsing content from {url}: {e}")

    # Return None if any error occurred during fetch/parse
    return None, None, None, None