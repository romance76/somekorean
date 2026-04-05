from bs4 import BeautifulSoup
import urllib.parse, re
from .base_scraper import BaseScraper
from utils.normalizer import normalize_phone, normalize_address, categorize_korean

class YellowPagesScraper(BaseScraper):
    BASE_URL = "https://www.yellowpages.com/search"

    def scrape_city_category(self, city, state, location, category, max_pages=3):
        results = []
        for page in range(1, max_pages + 1):
            params = {
                'search_terms': category,
                'geo_location_terms': location,
                'page': page
            }
            url = self.BASE_URL + '?' + urllib.parse.urlencode(params)
            print(f"  [YP] {category} in {city} (page {page})")
            r = self.fetch(url)
            if not r: break
            soup = BeautifulSoup(r.text, 'lxml')
            listings = soup.select('.result .info')
            if not listings: break
            for listing in listings:
                try:
                    name_el = listing.select_one('.business-name span')
                    if not name_el: continue
                    name = name_el.get_text(strip=True)
                    address_el = listing.select_one('.street-address')
                    locality_el = listing.select_one('.locality')
                    address = ''
                    if address_el: address = address_el.get_text(strip=True)
                    if locality_el: address += ', ' + locality_el.get_text(strip=True)
                    phone_el = listing.select_one('.phones.phone.primary')
                    phone = phone_el.get_text(strip=True) if phone_el else ''
                    website_el = listing.select_one('a.track-visit-website')
                    website = website_el.get('href', '') if website_el else ''
                    link_el = listing.select_one('a.business-name')
                    source_url = 'https://www.yellowpages.com' + link_el.get('href', '') if link_el else url
                    if not name: continue
                    results.append(self.normalize_result(
                        name_en=name,
                        category=categorize_korean(name, category),
                        address=normalize_address(address),
                        phone=normalize_phone(phone),
                        website=website,
                        region=city,
                        source='yellowpages',
                        source_url=source_url
                    ))
                except Exception as e:
                    print(f"    [PARSE ERROR] {e}")
            print(f"    Found {len(listings)} listings on page {page}")
        return results
