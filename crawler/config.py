import os
from dotenv import load_dotenv
load_dotenv()

CITIES = [
    # (city_name, state, search_location, region_tag)
    ("Los Angeles", "CA", "Los Angeles, CA", "LA"),
    ("Koreatown LA", "CA", "Koreatown, Los Angeles, CA", "LA"),
    ("Garden Grove", "CA", "Garden Grove, CA", "LA"),
    ("Rowland Heights", "CA", "Rowland Heights, CA", "LA"),
    ("San Francisco", "CA", "San Francisco, CA", "SF"),
    ("Daly City", "CA", "Daly City, CA", "SF"),
    ("San Jose", "CA", "San Jose, CA", "SF"),
    ("Seattle", "WA", "Seattle, WA", "Seattle"),
    ("Bellevue", "WA", "Bellevue, WA", "Seattle"),
    ("San Diego", "CA", "San Diego, CA", "SanDiego"),
    ("Las Vegas", "NV", "Las Vegas, NV", "LasVegas"),
    ("Sacramento", "CA", "Sacramento, CA", "Sacramento"),
    ("Portland", "OR", "Portland, OR", "Portland"),
    ("Honolulu", "HI", "Honolulu, HI", "Honolulu"),
    ("New York", "NY", "Flushing, Queens, NY", "NY"),
    ("Manhattan", "NY", "Manhattan, New York, NY", "NY"),
    ("Fort Lee", "NJ", "Fort Lee, NJ", "NY"),
    ("Palisades Park", "NJ", "Palisades Park, NJ", "NY"),
    ("Washington DC", "DC", "Annandale, VA", "DC"),
    ("Centreville", "VA", "Centreville, VA", "DC"),
    ("Rockville", "MD", "Rockville, MD", "DC"),
    ("Boston", "MA", "Boston, MA", "Boston"),
    ("Philadelphia", "PA", "Philadelphia, PA", "Philly"),
    ("Atlanta", "GA", "Doraville, GA", "Atlanta"),
    ("Duluth", "GA", "Duluth, GA", "Atlanta"),
    ("Norcross", "GA", "Norcross, GA", "Atlanta"),
    ("Houston", "TX", "Houston, TX", "Houston"),
    ("Dallas", "TX", "Dallas, TX", "Dallas"),
    ("Carrollton", "TX", "Carrollton, TX", "Dallas"),
    ("Charlotte", "NC", "Charlotte, NC", "Charlotte"),
    ("Miami", "FL", "Miami, FL", "Miami"),
    ("Chicago", "IL", "Chicago, IL", "Chicago"),
    ("Detroit", "MI", "Troy, MI", "Detroit"),
    ("Columbus", "OH", "Columbus, OH", "Columbus"),
    ("Minneapolis", "MN", "Minneapolis, MN", "Minneapolis"),
    ("Denver", "CO", "Denver, CO", "Denver"),
    ("Nashville", "TN", "Nashville, TN", "Nashville"),
    ("Baltimore", "MD", "Baltimore, MD", "Baltimore"),
]

CATEGORIES = [
    "Korean Restaurant",
    "Korean Grocery",
    "Korean BBQ",
    "Korean Market",
    "Korean Hair Salon",
    "Korean Spa",
    "Korean Church",
    "Korean Bakery",
    "Korean Real Estate",
    "Korean Insurance",
    "Korean Doctor",
    "Korean Dentist",
    "Korean Law",
    "Korean Accounting",
    "Korean Beauty Supply",
    "Korean Auto Repair",
    "Korean Travel Agency",
    "Korean School",
    "Korean Tutoring",
    "Korean Dry Cleaning",
    "Korean Taekwondo",
    "Korean Karaoke",
    "Korean Pharmacy",
    "Korean Bank",
    "Korean Cafe",
]

RATE_LIMIT_SECONDS = 2.0
MAX_PAGES_PER_SEARCH = 5
OUTPUT_DIR = "output"
DB_CACHE_FILE = "cache/geocode_cache.json"

API_ENDPOINT = os.getenv('SK_API_URL', 'https://somekorean.com/api/admin/businesses/import')
API_TOKEN = os.getenv('SK_API_TOKEN', '')
