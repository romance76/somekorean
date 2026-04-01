import time, random, requests
from abc import ABC, abstractmethod
from urllib.robotparser import RobotFileParser

class BaseScraper(ABC):
    def __init__(self, rate_limit=2.0):
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self._last_request = 0

    def fetch(self, url, **kwargs):
        elapsed = time.time() - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed + random.uniform(0.1, 0.5))
        try:
            r = self.session.get(url, timeout=15, **kwargs)
            self._last_request = time.time()
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            print(f"  [FETCH ERROR] {url}: {e}")
            return None

    @abstractmethod
    def scrape_city_category(self, city: str, state: str, location: str, category: str) -> list:
        pass

    def normalize_result(self, **kwargs) -> dict:
        return {
            'name_en': kwargs.get('name_en', '').strip(),
            'name_ko': kwargs.get('name_ko', ''),
            'category': kwargs.get('category', '\uae30\ud0c0'),
            'address': kwargs.get('address', '').strip(),
            'phone': kwargs.get('phone', '').strip(),
            'website': kwargs.get('website', ''),
            'hours': kwargs.get('hours', {}),
            'region': kwargs.get('region', ''),
            'source': kwargs.get('source', 'unknown'),
            'source_url': kwargs.get('source_url', ''),
            'lat': kwargs.get('lat'),
            'lng': kwargs.get('lng'),
            'data_source': 'crawler',
        }
