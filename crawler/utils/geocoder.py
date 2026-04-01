import json, os, time, requests
from pathlib import Path

class Geocoder:
    def __init__(self, cache_file='cache/geocode_cache.json'):
        Path('cache').mkdir(exist_ok=True)
        self.cache_file = cache_file
        self.cache = {}
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                self.cache = json.load(f)

    def geocode(self, address: str):
        if address in self.cache:
            return self.cache[address]
        time.sleep(1.1)  # Nominatim 1 req/sec limit
        try:
            url = 'https://nominatim.openstreetmap.org/search'
            headers = {'User-Agent': 'SomeKorean/1.0 contact@somekorean.com'}
            params = {'q': address, 'format': 'json', 'limit': 1, 'countrycodes': 'us'}
            r = requests.get(url, params=params, headers=headers, timeout=10)
            data = r.json()
            if data:
                result = {'lat': float(data[0]['lat']), 'lng': float(data[0]['lon'])}
                self.cache[address] = result
                self._save_cache()
                return result
        except Exception as e:
            print(f"Geocode error for {address}: {e}")
        self.cache[address] = None
        self._save_cache()
        return None

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
