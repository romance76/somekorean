#!/usr/bin/env python3
"""
SomeKorean Business Crawler
Usage: python main.py [--city "Los Angeles"] [--category "Korean Restaurant"] [--all] [--import]
"""
import argparse, json, os, sys
from pathlib import Path
from config import CITIES, CATEGORIES, RATE_LIMIT_SECONDS
from scrapers.yellowpages_scraper import YellowPagesScraper
from pipeline.deduplicator import deduplicate
from pipeline.importer import Importer
from utils.geocoder import Geocoder
from utils.normalizer import normalize_phone

Path('output').mkdir(exist_ok=True)
Path('cache').mkdir(exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='SomeKorean Business Crawler')
    parser.add_argument('--city', help='Specific city to crawl')
    parser.add_argument('--category', help='Specific category')
    parser.add_argument('--all', action='store_true', help='Crawl all cities and categories')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import to server')
    parser.add_argument('--geocode', action='store_true', help='Geocode addresses')
    parser.add_argument('--limit', type=int, default=3, help='Max pages per search')
    args = parser.parse_args()

    scraper = YellowPagesScraper(rate_limit=RATE_LIMIT_SECONDS)
    geocoder = Geocoder()
    importer = Importer(
        api_url=os.getenv('SK_API_URL', 'https://somekorean.com/api/admin/businesses/import'),
        api_token=os.getenv('SK_API_TOKEN', '')
    )

    all_results = []

    # Determine cities/categories to crawl
    if args.city:
        cities = [c for c in CITIES if args.city.lower() in c[0].lower()]
        if not cities:
            print(f"City '{args.city}' not found in config")
            sys.exit(1)
    elif args.all:
        cities = CITIES
    else:
        cities = CITIES[:3]  # Default: first 3 cities

    categories = [args.category] if args.category else CATEGORIES[:5]  # Default: first 5 categories

    print(f"Crawling {len(cities)} cities x {len(categories)} categories = {len(cities)*len(categories)} searches")

    for city_name, state, location, region in cities:
        city_results = []
        for category in categories:
            print(f"\n[CRAWL] {category} in {city_name}, {state}")
            try:
                results = scraper.scrape_city_category(city_name, state, location, category, max_pages=args.limit)
                print(f"  -> {len(results)} results")
                city_results.extend(results)
            except Exception as e:
                print(f"  [ERROR] {e}")

        # Deduplicate city results
        city_unique = deduplicate(city_results)
        all_results.extend(city_unique)
        print(f"\n[CITY DONE] {city_name}: {len(city_unique)} unique businesses")

    # Global dedup
    all_unique = deduplicate(all_results)
    print(f"\n[TOTAL] {len(all_unique)} unique businesses across all cities")

    # Geocode if requested
    if args.geocode:
        print("\nGeocoding addresses...")
        for biz in all_unique:
            if not biz.get('lat') and biz.get('address'):
                coords = geocoder.geocode(biz['address'])
                if coords:
                    biz['lat'] = coords['lat']
                    biz['lng'] = coords['lng']

    # Save to JSON
    output_file = importer.save_to_json(all_unique, 'korean_businesses_all_cities.json')

    # Also save by region
    regions = {}
    for biz in all_unique:
        r = biz.get('region', 'Unknown')
        regions.setdefault(r, []).append(biz)
    for region, bizdatas in regions.items():
        importer.save_to_json(bizdatas, f'businesses_{region.lower().replace(" ","_")}.json')

    print(f"\nSaved to: {output_file}")
    print("Regions:", {r: len(b) for r, b in regions.items()})

    # Import to server
    if args.do_import:
        print("\nImporting to SomeKorean server...")
        importer.import_batch(all_unique)

    return all_unique

if __name__ == '__main__':
    main()
