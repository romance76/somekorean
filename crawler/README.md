# SomeKorean Business Crawler

Team 3 (Crawler Gamma) — 미국 전역 한인 비즈니스 데이터 수집기

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Test with 3 cities, 5 categories (default)
python main.py

# Specific city
python main.py --city "Los Angeles"

# Specific category
python main.py --category "Korean Restaurant"

# Specific city + category
python main.py --city "New York" --category "Korean BBQ"

# All cities + all categories
python main.py --all

# With geocoding (adds lat/lng via Nominatim)
python main.py --all --geocode

# Import to SomeKorean server (requires SK_API_TOKEN in .env)
python main.py --all --import

# Limit pages per search (default: 3)
python main.py --all --limit 5
```

## Environment Variables (.env)

```
SK_API_URL=https://somekorean.com/api/admin/businesses/import
SK_API_TOKEN=your_admin_jwt_token
```

## Cities Covered (38 locations across 22+ metro areas)

| Region | Locations |
|--------|-----------|
| LA | Los Angeles, Koreatown, Garden Grove, Rowland Heights |
| SF Bay | San Francisco, Daly City, San Jose |
| Seattle | Seattle, Bellevue |
| Other West | San Diego, Las Vegas, Sacramento, Portland, Honolulu |
| New York | Flushing/Queens, Manhattan, Fort Lee NJ, Palisades Park NJ |
| DC | Annandale VA, Centreville VA, Rockville MD |
| East | Boston, Philadelphia, Baltimore |
| Atlanta | Doraville, Duluth, Norcross |
| Texas | Houston, Dallas, Carrollton |
| Other South | Charlotte, Miami, Nashville |
| Midwest | Chicago, Troy MI, Columbus, Minneapolis, Denver |

## Categories (25 total)

Korean Restaurant, Grocery, BBQ, Market, Hair Salon, Spa, Church, Bakery,
Real Estate, Insurance, Doctor, Dentist, Law, Accounting, Beauty Supply,
Auto Repair, Travel Agency, School, Tutoring, Dry Cleaning, Taekwondo,
Karaoke, Pharmacy, Bank, Cafe

## Output Files

```
output/
  korean_businesses_all_cities.json   # All businesses combined
  businesses_LA.json                  # LA metro businesses
  businesses_NY.json                  # NY metro businesses
  businesses_DC.json                  # DC metro businesses
  businesses_Atlanta.json             # Atlanta metro businesses
  businesses_<region>.json            # Per-region files
cache/
  geocode_cache.json                  # Cached geocoding results
```

## Output JSON Schema

```json
{
  "name_en": "Seoul Garden Korean Restaurant",
  "name_ko": "",
  "category": "식당",
  "address": "1234 Olympic Blvd, Los Angeles, CA 90006",
  "phone": "(213) 555-1234",
  "website": "https://seoulgardenla.com",
  "hours": {},
  "region": "Los Angeles",
  "source": "yellowpages",
  "source_url": "https://www.yellowpages.com/...",
  "lat": 34.0522,
  "lng": -118.2437,
  "data_source": "crawler"
}
```

## Architecture

```
crawler/
  main.py                    # Entry point + orchestrator
  config.py                  # Cities, categories, settings
  requirements.txt
  scrapers/
    base_scraper.py          # Abstract base class with rate limiting
    yellowpages_scraper.py   # YellowPages.com scraper
    koreatimes_scraper.py    # Korea Times yellow pages scraper
  utils/
    geocoder.py              # Nominatim geocoding with cache
    normalizer.py            # Phone/address/category normalization
  pipeline/
    deduplicator.py          # Fuzzy duplicate detection
    importer.py              # JSON export + server API import
  output/                    # JSON output files
  cache/                     # Geocoding cache
```

## Server API Endpoint

The crawler imports to:
`POST /api/admin/businesses/import`

Required headers:
- `Authorization: Bearer <SK_API_TOKEN>`
- `Content-Type: application/json`

Payload: `{ "businesses": [...] }`

Response: `{ "inserted": N, "updated": N, "skipped": N, "total": N }`
