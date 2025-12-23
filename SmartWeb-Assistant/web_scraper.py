import os
import time
import logging
import requests
import html2text
from bs4 import BeautifulSoup
from web_crawler import get_random_proxy, get_urls_from_file

# Configure logging
logger = logging.getLogger(__name__)

def extract_body_content(soup):
    try:
        body = soup.find('body')
        if not body:
            return None
        tags_to_remove = ['script', 'nav', 'footer', 'video', 'button', 'svg', 'img']
        for tag in tags_to_remove:
            for element in body.find_all(tag):
                element.decompose()
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0
        markdown_text = h.handle(str(body))
        return markdown_text
    except Exception as e:
        logger.error(f"Error extracting body content: {str(e)}")
        return None

def scrape_page(url):
    max_retries = 3
    retries = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    while retries < max_retries:
        try:
            proxies = get_random_proxy()
            logger.info(f"Using proxy {proxies['http']} for scraping {url}")
            response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            body_content = extract_body_content(soup)
            title = soup.title.string if soup.title else 'No Title'
            return {
                'url': url,
                'title': title.strip(),
                'content': body_content
            }
        except Exception as e:
            retries += 1
            logger.error(f"Error scraping {url} with proxy {proxies['http']}: {str(e)}. Retry {retries}/{max_retries}")
            if retries == max_retries:
                logger.error(f"Max retries reached for {url}. Skipping.")
                return None
            time.sleep(2)

def save_content(data, output_dir, index):
    if not data or not data['content']:
        return
    os.makedirs(output_dir, exist_ok=True)
    filename = f"page_{index}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data['content'])
    logger.info(f"Saved content to {filepath}")

def scrape_website(url_file, output_dir):
    urls = get_urls_from_file(url_file)
    logger.info(f"Found {len(urls)} URLs in file")
    for i, url in enumerate(urls, 1):
        logger.info(f"Processing {i}/{len(urls)}: {url}")
        data = scrape_page(url)
        if data and data['content']:
            save_content(data, output_dir, i)
        time.sleep(2)
    logger.info("Scraping completed")

def clear_scraped_data(scraped_dir):
    try:
        for file in os.listdir(scraped_dir):
            file_path = os.path.join(scraped_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        logger.info(f"Cleared scraped data directory: {scraped_dir}")
    except Exception as e:
        logger.error(f"Error clearing scraped data directory: {str(e)}")
        raise
