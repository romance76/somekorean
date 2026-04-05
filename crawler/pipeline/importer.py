import json, requests, os
from pathlib import Path

class Importer:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token

    def save_to_json(self, businesses: list, filename: str):
        Path('output').mkdir(exist_ok=True)
        filepath = f"output/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(businesses, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(businesses)} businesses to {filepath}")
        return filepath

    def import_to_server(self, businesses: list) -> dict:
        if not self.api_token:
            print("No API token set - saving to file only")
            return {'error': 'no_token'}
        try:
            r = requests.post(
                self.api_url,
                json={'businesses': businesses},
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            return r.json()
        except Exception as e:
            return {'error': str(e)}

    def import_batch(self, businesses: list, batch_size=100):
        total_inserted = 0
        for i in range(0, len(businesses), batch_size):
            batch = businesses[i:i+batch_size]
            result = self.import_to_server(batch)
            inserted = result.get('inserted', 0)
            total_inserted += inserted
            print(f"  Batch {i//batch_size + 1}: {inserted} inserted, {result.get('skipped', 0)} skipped")
        return total_inserted
