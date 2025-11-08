"""
IndexNow Auto Submitter
Automatically submits new URLs from your sitemap to IndexNow API.
Only submits URLs that haven't been submitted before.

Author: Gaviru Bihan
License: MIT
Repository: https://github.com/gavirubihan/indexnow-auto-submit
"""

import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

# ========== CONFIGURATION ==========
# IMPORTANT: Update these values before running!

API_KEY = "your-api-key-here"  # Your IndexNow API key
SITE_URL = "https://yourdomain.com"  # Your website URL (with https://)
SITEMAP_URL = "https://yourdomain.com/sitemap.xml"  # Your sitemap URL

# File paths
LOG_FILE = "indexnow_log.txt"
URLS_FILE = "urls_to_submit.txt"
SUBMITTED_URLS_FILE = "submitted_urls.txt"

# IndexNow endpoint (don't change unless necessary)
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

# ========== END CONFIGURATION ==========

# Configure session
session = requests.Session()
session.trust_env = False


def log_message(message):
    """Log message with timestamp to file and console."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(log_entry + "\n")
    
    print(log_entry)


def fetch_sitemap_urls(sitemap_url):
    """
    Fetch all URLs from sitemap.xml.
    Supports sitemap indexes and recursive sub-sitemaps.
    
    Args:
        sitemap_url (str): URL of the sitemap
        
    Returns:
        list: List of URLs found in the sitemap
    """
    log_message(f"Fetching sitemap from {sitemap_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = session.get(sitemap_url, timeout=30, headers=headers)
        
        if response.status_code != 200:
            log_message(f"Failed to fetch sitemap: HTTP {response.status_code}")
            return []
        
        # Parse XML
        root = ET.fromstring(response.text)
        urls = []
        
        # Define XML namespaces
        namespaces = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'xhtml': 'http://www.w3.org/1999/xhtml',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
            'video': 'http://www.google.com/schemas/sitemap-video/1.1'
        }
        
        # Try to find URLs with namespace
        for url_elem in root.findall('sm:url', namespaces):
            loc_elem = url_elem.find('sm:loc', namespaces)
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
        
        # Fallback: try without namespace
        if not urls:
            for url_elem in root.findall('.//url'):
                loc_elem = url_elem.find('loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())
        
        # Check if this is a sitemap index (contains sub-sitemaps)
        if not urls:
            for sitemap_elem in root.findall('sm:sitemap', namespaces):
                loc_elem = sitemap_elem.find('sm:loc', namespaces)
                if loc_elem is not None and loc_elem.text:
                    log_message(f"Found sub-sitemap: {loc_elem.text}")
                    # Recursively fetch sub-sitemap URLs
                    sub_urls = fetch_sitemap_urls(loc_elem.text.strip())
                    urls.extend(sub_urls)
                    time.sleep(1)  # Be nice to the server
        
        if urls:
            log_message(f"Found {len(urls)} URLs in sitemap.")
        else:
            log_message("No URLs found in sitemap.")
            
        return urls
        
    except ET.ParseError as e:
        log_message(f"XML parsing error: {e}")
        return []
    except requests.exceptions.Timeout:
        log_message("Request timed out")
        return []
    except requests.exceptions.ConnectionError as e:
        log_message(f"Connection error: {e}")
        return []
    except Exception as e:
        log_message(f"Error fetching sitemap: {e}")
        import traceback
        log_message(traceback.format_exc())
        return []


def load_submitted_urls():
    """
    Load previously submitted URLs from tracking file.
    
    Returns:
        set: Set of previously submitted URLs
    """
    try:
        with open(SUBMITTED_URLS_FILE, "r", encoding="utf-8") as f:
            urls = set(line.strip() for line in f if line.strip())
        log_message(f"Loaded {len(urls)} previously submitted URLs")
        return urls
    except FileNotFoundError:
        log_message("No previous submission history found. This is the first run.")
        return set()
    except Exception as e:
        log_message(f"Error loading submitted URLs: {e}")
        return set()


def save_submitted_urls(urls):
    """
    Append newly submitted URLs to tracking file.
    
    Args:
        urls (list): List of URLs to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(SUBMITTED_URLS_FILE, "a", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        log_message(f"Added {len(urls)} URLs to submission history")
        return True
    except Exception as e:
        log_message(f"Error saving submitted URLs: {e}")
        return False


def get_new_urls(all_urls, submitted_urls):
    """
    Compare sitemap URLs with submitted URLs to find new ones.
    
    Args:
        all_urls (list): All URLs from sitemap
        submitted_urls (set): Previously submitted URLs
        
    Returns:
        list: List of new URLs
    """
    all_urls_set = set(all_urls)
    new_urls = all_urls_set - submitted_urls
    return list(new_urls)


def save_urls_to_file(urls, filename):
    """
    Save URLs to text file (overwrites existing file).
    
    Args:
        urls (list): List of URLs to save
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        log_message(f"Saved {len(urls)} URLs to {filename}")
        return True
    except Exception as e:
        log_message(f"Error saving URLs to file: {e}")
        return False


def load_urls_from_file(filename):
    """
    Load URLs from text file.
    
    Args:
        filename (str): Input filename
        
    Returns:
        list: List of URLs
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        log_message(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        log_message(f"File not found: {filename}")
        return []
    except Exception as e:
        log_message(f"Error loading URLs from file: {e}")
        return []


def submit_to_indexnow(urls):
    """
    Submit URLs to IndexNow API in bulk.
    Maximum 10,000 URLs per request.
    
    Args:
        urls (list): List of URLs to submit
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not urls:
        log_message("No URLs to submit")
        return False
    
    # IndexNow has a limit of 10,000 URLs per request
    if len(urls) > 10000:
        log_message(f"WARNING: You have {len(urls)} URLs. IndexNow allows max 10,000 per request.")
        log_message("Submitting first 10,000 URLs only.")
        urls = urls[:10000]
    
    # Prepare payload
    payload = {
        "host": SITE_URL.replace("https://", "").replace("http://", ""),
        "key": API_KEY,
        "keyLocation": f"{SITE_URL}/{API_KEY}.txt",
        "urlList": urls
    }

    try:
        log_message(f"Submitting {len(urls)} URLs to IndexNow...")
        response = session.post(INDEXNOW_ENDPOINT, json=payload, timeout=60)
        status = response.status_code

        if status == 200 or status == 202:
            log_message(f"✓ SUCCESS: {len(urls)} URLs submitted successfully (HTTP {status})")
            return True
        elif status == 400:
            log_message(f"✗ ERROR 400: Bad Request - Invalid payload format")
            log_message(f"Response: {response.text}")
            return False
        elif status == 403:
            log_message(f"✗ ERROR 403: Forbidden - Invalid or missing key file")
            log_message(f"Make sure {SITE_URL}/{API_KEY}.txt exists and contains: {API_KEY}")
            return False
        elif status == 422:
            log_message(f"✗ ERROR 422: Unprocessable Entity - URLs don't match host or key mismatch")
            log_message(f"Response: {response.text}")
            return False
        elif status == 429:
            log_message(f"⚠ ERROR 429: Too Many Requests - Rate limited")
            log_message("Waiting 5 minutes before retry...")
            time.sleep(300)
            return submit_to_indexnow(urls)
        else:
            log_message(f"✗ Unexpected error HTTP {status}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        log_message("✗ Request timed out. Try reducing the number of URLs or check your connection.")
        return False
    except Exception as e:
        log_message(f"✗ Exception occurred: {e}")
        import traceback
        log_message(traceback.format_exc())
        return False


def validate_configuration():
    """
    Validate that configuration has been updated from defaults.
    
    Returns:
        bool: True if valid, False otherwise
    """
    if API_KEY == "your-api-key-here":
        log_message("ERROR: Please update API_KEY in the configuration section!")
        return False
    
    if "yourdomain.com" in SITE_URL:
        log_message("ERROR: Please update SITE_URL in the configuration section!")
        return False
    
    if "yourdomain.com" in SITEMAP_URL:
        log_message("ERROR: Please update SITEMAP_URL in the configuration section!")
        return False
    
    return True


def main():
    """Main execution function."""
    log_message("=" * 60)
    log_message("IndexNow Auto Submitter - Starting")
    log_message("=" * 60)
    
    # Validate configuration
    if not validate_configuration():
        log_message("Please update the configuration section at the top of the script.")
        log_message("=" * 60 + "\n")
        return
    
    # Step 1: Fetch URLs from sitemap
    log_message("\nStep 1: Fetching URLs from sitemap...")
    all_urls = fetch_sitemap_urls(SITEMAP_URL)

    if not all_urls:
        log_message("No URLs found in sitemap. Exiting.")
        log_message("=" * 60 + "\n")
        return

    log_message(f"Total URLs in sitemap: {len(all_urls)}")

    # Step 2: Load previously submitted URLs
    log_message("\nStep 2: Loading submission history...")
    submitted_urls = load_submitted_urls()

    # Step 3: Find new URLs
    log_message("\nStep 3: Identifying new URLs...")
    new_urls = get_new_urls(all_urls, submitted_urls)
    
    if not new_urls:
        log_message("✓ No new URLs found. All URLs have been previously submitted.")
        log_message("=" * 60 + "\n")
        return
    
    log_message(f"Found {len(new_urls)} NEW URLs to submit")

    # Step 4: Save new URLs to text file
    log_message(f"\nStep 4: Saving new URLs to {URLS_FILE}...")
    if not save_urls_to_file(new_urls, URLS_FILE):
        log_message("Failed to save URLs. Exiting.")
        log_message("=" * 60 + "\n")
        return

    # Step 5: Load URLs from text file (verification step)
    log_message(f"\nStep 5: Loading URLs from {URLS_FILE}...")
    urls_to_submit = load_urls_from_file(URLS_FILE)

    if not urls_to_submit:
        log_message("No URLs loaded from file. Exiting.")
        log_message("=" * 60 + "\n")
        return

    # Step 6: Submit new URLs to IndexNow
    log_message(f"\nStep 6: Submitting new URLs to IndexNow...")
    success = submit_to_indexnow(urls_to_submit)

    # Step 7: Update submission history if successful
    if success:
        log_message("\nStep 7: Updating submission history...")
        save_submitted_urls(urls_to_submit)
    else:
        log_message("\nSubmission failed. URLs not added to history.")
        log_message("You can retry by running the script again.")

    # Summary
    log_message("\n" + "=" * 60)
    log_message("Submission Summary")
    log_message("=" * 60)
    log_message(f"Total URLs in sitemap: {len(all_urls)}")
    log_message(f"Previously submitted: {len(submitted_urls)}")
    log_message(f"New URLs found: {len(new_urls)}")
    log_message(f"Submission status: {'✓ SUCCESS' if success else '✗ FAILED'}")
    log_message(f"New URLs file: {URLS_FILE}")
    log_message(f"History file: {SUBMITTED_URLS_FILE}")
    log_message("=" * 60 + "\n")


if __name__ == "__main__":
    main()