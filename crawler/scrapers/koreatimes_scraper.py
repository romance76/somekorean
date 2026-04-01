from bs4 import BeautifulSoup
import urllib.parse
from .base_scraper import BaseScraper
from utils.normalizer import normalize_phone, normalize_address, categorize_korean

class KoreaTimesScraper(BaseScraper):
    """Scrape Korea Times LA yellow pages"""

    def scrape_city_category(self, city, state, location, category, max_pages=3):
        results = []
        # Korea Times yellow pages
        base_urls = [
            f"https://www.koreadaily.com/yellow_page/list.asp",
            f"https://www.koreatimes.com/yellow-pages/",
        ]
        for base_url in base_urls:
            try:
                print(f"  [KT] Trying {base_url}")
                r = self.fetch(base_url)
                if r and r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    # Parse whatever structure exists
                    listings = soup.select('.listing, .business, .yp-item, tr[class*="list"]')
                    for item in listings[:50]:
                        text = item.get_text(strip=True)
                        if len(text) > 5:
                            print(f"    Item: {text[:80]}")
            except Exception as e:
                print(f"    Error: {e}")
        return results
