import os
import random
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
import time

# Configure logging
logger = logging.getLogger(__name__)

# Proxy list
PROXIES = [
    {"ip": "38.153.152.244", "port": "9594", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "86.38.234.176", "port": "6630", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "173.211.0.148", "port": "6641", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "161.123.152.115", "port": "6360", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "216.10.27.159", "port": "6837", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "154.36.110.199", "port": "6853", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "45.151.162.198", "port": "6600", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "185.199.229.156", "port": "7492", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "185.199.228.220", "port": "7300", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
    {"ip": "185.199.231.45", "port": "8382", "username": "tfkzunmh", "password": "c0cwpmv652l8"},
]

def get_random_proxy():
    """Select a random proxy from the proxy list."""
    proxy = random.choice(PROXIES)
    proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
    logger.info(f"Using proxy url: {proxy_url}")
    return {
        "http": proxy_url,
        "https": proxy_url
    }

class WebCrawlerURLs:
    def __init__(self, start_url, output_file):
        self.start_url = start_url
        self.visited = set()
        self.queue = deque([start_url])
        self.all_urls = set([start_url])
        self.domain = urlparse(start_url).netloc
        self.base_url = f"https://{self.domain}/"
        self.output_file = output_file

    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)
            return (parsed.scheme in ['http', 'https'] and parsed.netloc == self.domain and '/blog' not in parsed.path.lower())
        except:
            return False

    def extract_links(self, soup, current_url):
        unique_links = set()
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                absolute_url = urljoin(current_url, href)
                parsed_url = urlparse(absolute_url)
                clean_url = urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    ''
                ))
                if (clean_url.startswith(self.base_url) or clean_url.startswith(f"http://{self.domain}/")) and \
                   self.is_valid_url(clean_url) and \
                   clean_url not in self.visited:
                    unique_links.add(clean_url)
        return unique_links

    def crawl_urls(self):
        max_retries = 3
        while self.queue:
            current_url = self.queue.popleft()
            if current_url in self.visited:
                continue
            retries = 0
            while retries < max_retries:
                try:
                    proxies = get_random_proxy()
                    logger.info(f"Using proxy {proxies['http']} for {current_url}")
                    response = requests.get(current_url, timeout=5, proxies=proxies)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.visited.add(current_url)
                    new_links = self.extract_links(soup, current_url)
                    for link in new_links:
                        if link not in self.all_urls:
                            self.all_urls.add(link)
                            self.queue.append(link)
                    logger.info(f"Processed: {current_url} | Queue size: {len(self.queue)} | Total URLs: {len(self.all_urls)}")
                    time.sleep(1)
                    break
                except requests.RequestException as e:
                    retries += 1
                    logger.error(f"Failed to process {current_url} with proxy {proxies['http']} : {e}. Retry {retries}/{max_retries}")
                    if retries == max_retries:
                        logger.error(f"Max retries reached for {current_url}. Skipping.")
                        break
                    time.sleep(2)

    def save_urls_to_file(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for url in sorted(self.all_urls):
                f.write(f"{url}\n")
        logger.info(f"URLs saved to {self.output_file}")

def get_urls_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except Exception as e:
        logger.error(f"Error reading URLs from file: {str(e)}")
        return []
