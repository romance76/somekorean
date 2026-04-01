import paramiko, sys, base64, os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR:'+e) if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

# STEP 1: Create crawler directory on server
print(ssh('mkdir -p /var/www/somekorean/crawler_server'))

# STEP 2: Install Python deps on server
print("Installing Python deps...")
print(ssh('pip3 install requests beautifulsoup4 pymysql 2>&1 | tail -5', timeout=120))

# STEP 3: Write server-side crawler (simplified, directly inserts to DB)
crawler_main = '''#!/usr/bin/env python3
"""
SomeKorean Server-Side Crawler
Runs on the server, directly inserts into MySQL
Usage: python3 crawler_server.py [--city "Los Angeles"] [--category "korean-restaurant"] [--limit 50]
"""
import sys, os, re, time, json, logging, argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pymysql

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/tmp/crawl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

DB_CONFIG = {
    'host': '127.0.0.1', 'port': 3306,
    'user': 'somekorean_user', 'password': 'SK_DB@2026!secure',
    'database': 'somekorean', 'charset': 'utf8mb4'
}

CITIES = [
    'Los Angeles,CA', 'New York,NY', 'Chicago,IL', 'Houston,TX',
    'Seattle,WA', 'Atlanta,GA', 'Dallas,TX', 'San Francisco,CA',
    'Washington,DC', 'Las Vegas,NV', 'Boston,MA', 'Philadelphia,PA',
    'Miami,FL', 'San Diego,CA', 'Denver,CO', 'Phoenix,AZ',
    'Minneapolis,MN', 'Detroit,MI', 'Portland,OR', 'Baltimore,MD',
    'Honolulu,HI', 'Annandale,VA', 'Fort Lee,NJ', 'Flushing,NY',
]

CATEGORIES = [
    'korean+restaurant', 'korean+grocery', 'korean+bbq', 'korean+spa',
    'korean+hair+salon', 'korean+real+estate', 'korean+lawyer',
    'korean+doctor', 'korean+insurance', 'korean+travel',
    'korean+church', 'korean+school', 'korean+market',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def clean_phone(p):
    if not p: return None
    digits = re.sub(r'\\D', '', p)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return p[:20] if p else None

def clean_text(t):
    if not t: return None
    return re.sub(r'\\s+', ' ', t).strip()[:500]

def scrape_yellowpages(city, category, limit=30):
    results = []
    city_slug = city.replace(',', '%2C').replace(' ', '+')
    cat_slug = category
    url = f"https://www.yellowpages.com/search?search_terms={cat_slug}&geo_location_terms={city_slug}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            log.warning(f"YP {city} {category}: HTTP {resp.status_code}")
            return results
        soup = BeautifulSoup(resp.text, 'html.parser')
        listings = soup.select('.result .info')[:limit]
        for item in listings:
            name_el = item.select_one('.business-name span')
            addr_el = item.select_one('.street-address')
            city_el = item.select_one('.locality')
            phone_el = item.select_one('.phones')
            cat_el = item.select_one('.categories a')
            website_el = item.select_one('a.track-visit-website')
            name = clean_text(name_el.get_text() if name_el else None)
            if not name: continue
            address_parts = []
            if addr_el: address_parts.append(clean_text(addr_el.get_text()))
            if city_el: address_parts.append(clean_text(city_el.get_text()))
            results.append({
                'name': name,
                'address': ', '.join(filter(None, address_parts)) or city,
                'phone': clean_phone(phone_el.get_text() if phone_el else None),
                'category': clean_text(cat_el.get_text() if cat_el else category.replace('+', ' ').title()),
                'website': website_el.get('href') if website_el else None,
                'data_source': 'yellowpages',
                'source_url': url,
                'region': city.split(',')[0].strip()
            })
        log.info(f"YP {city} [{category}]: {len(results)} results")
    except Exception as e:
        log.error(f"YP error {city} {category}: {e}")
    return results

def insert_businesses(businesses):
    if not businesses: return 0, 0
    inserted = skipped = 0
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        for biz in businesses:
            # Check duplicate
            cur.execute("SELECT id FROM businesses WHERE name=%s AND address=%s LIMIT 1",
                        (biz['name'], biz['address']))
            if cur.fetchone():
                skipped += 1
                continue
            try:
                cur.execute("""
                    INSERT INTO businesses
                    (name, category, address, phone, website, region,
                     data_source, source_url, status, is_active, created_at, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'active',1,%s,%s)
                """, (
                    biz['name'], biz.get('category','기타'), biz.get('address',''),
                    biz.get('phone'), biz.get('website'), biz.get('region'),
                    biz.get('data_source','crawler'), biz.get('source_url'),
                    datetime.now(), datetime.now()
                ))
                inserted += 1
            except Exception as e:
                log.error(f"Insert error: {e}")
                skipped += 1
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"DB connection error: {e}")
    return inserted, skipped

def write_status(status, inserted, skipped, current, total, message=''):
    status_data = {
        'status': status,
        'inserted': inserted,
        'skipped': skipped,
        'progress': f"{current}/{total}",
        'message': message,
        'updated_at': datetime.now().isoformat()
    }
    with open('/tmp/crawl_status.json', 'w') as f:
        json.dump(status_data, f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', default='all', help='City to crawl (or "all")')
    parser.add_argument('--category', default='all', help='Category (or "all")')
    parser.add_argument('--limit', type=int, default=30, help='Results per query')
    args = parser.parse_args()

    cities = CITIES if args.city == 'all' else [args.city]
    categories = CATEGORIES if args.category == 'all' else [args.category.replace(' ', '+')]
    total_jobs = len(cities) * len(categories)
    total_inserted = total_skipped = job_num = 0

    log.info(f"Starting crawl: {len(cities)} cities x {len(categories)} categories = {total_jobs} jobs")
    write_status('running', 0, 0, 0, total_jobs, 'Crawling started...')

    for city in cities:
        for category in categories:
            job_num += 1
            write_status('running', total_inserted, total_skipped, job_num, total_jobs,
                         f"[{job_num}/{total_jobs}] {city} - {category}")
            businesses = scrape_yellowpages(city, category, args.limit)
            ins, skip = insert_businesses(businesses)
            total_inserted += ins
            total_skipped += skip
            log.info(f"Progress [{job_num}/{total_jobs}]: +{ins} inserted, {skip} skipped (total: {total_inserted})")
            time.sleep(1.2)  # Rate limiting: 1 req/sec

    msg = f"완료! 총 {total_inserted}개 업소 추가, {total_skipped}개 중복 건너뜀"
    log.info(msg)
    write_status('done', total_inserted, total_skipped, total_jobs, total_jobs, msg)

if __name__ == '__main__':
    main()
'''

print("Writing server crawler...")
print(write_file('/var/www/somekorean/crawler_server/crawler.py', crawler_main))
print(ssh('chmod +x /var/www/somekorean/crawler_server/crawler.py'))

# STEP 4: Test DB connection
test_db = '''import pymysql
try:
    conn = pymysql.connect(host="127.0.0.1", user="somekorean_user",
        password="SK_DB@2026!secure", database="somekorean", charset="utf8mb4")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM businesses")
    print("DB OK, businesses:", cur.fetchone()[0])
    conn.close()
except Exception as e:
    print("DB ERROR:", e)
'''
print("Testing DB connection...")
print(write_file('/tmp/test_db.py', test_db))
print(ssh('python3 /tmp/test_db.py'))

# STEP 5: Update AdminBusinessController bulkImport to trigger server crawler
raw = ssh('base64 /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php')
content = base64.b64decode(raw).decode('utf-8')

old_method = '''    // POST /api/admin/businesses/import (bulk import from crawler or manual trigger)
    public function bulkImport(Request $req)
    {
        // Manual trigger from admin UI - return crawl instructions
        if ($req->input('trigger') === 'manual') {
            $city = $req->input('city', 'all');
            $category = $req->input('category', 'all');
            $cityLabel = $city === 'all' ? '전체 38개 도시' : $city;
            $catLabel = $category === 'all' ? '전체 카테고리' : $category;
            $total = DB::table('businesses')->count();
            return response()->json([
                'message' => "크롤링 설정이 저장되었습니다.\\n\\n서버에서 다음 명령어로 크롤링을 실행하세요:\\n\\n  python crawler/main.py --all\\n\\n또는 특정 도시/카테고리:\\n  python crawler/main.py --city \\"Los Angeles\\" --category korean-restaurant\\n\\n현재 업소 수: {$total}개",
                'city' => $cityLabel,
                'category' => $catLabel,
                'current_total' => $total,
                'status' => 'queued'
            ]);
        }

        // Actual bulk import from crawler API call
        $businesses = $req->input('businesses', []);
        if (empty($businesses)) {
            return response()->json(['message' => '가져올 업소 데이터가 없습니다.', 'inserted' => 0, 'skipped' => 0], 200);
        }
        $inserted = 0; $skipped = 0;
        foreach ($businesses as $biz) {
            $name = $biz['name_en'] ?? $biz['name_ko'] ?? $biz['name'] ?? '';
            if (!$name) { $skipped++; continue; }
            $exists = DB::table('businesses')->where('name', $name)->where('address', $biz['address'] ?? '')->exists();
            if ($exists) { $skipped++; continue; }
            DB::table('businesses')->insert([
                'name' => $name, 'name_ko' => $biz['name_ko'] ?? null, 'name_en' => $biz['name_en'] ?? null,
                'category' => $biz['category'] ?? '기타', 'address' => $biz['address'] ?? '',
                'phone' => $biz['phone'] ?? null, 'website' => $biz['website'] ?? null,
                'lat' => $biz['lat'] ?? null, 'lng' => $biz['lng'] ?? null,
                'region' => $biz['region'] ?? null, 'data_source' => 'crawler',
                'source_url' => $biz['source_url'] ?? null, 'status' => 'active',
                'is_active' => 1, 'created_at' => now(), 'updated_at' => now(),
            ]);
            $inserted++;
        }
        return response()->json([
            'message' => "{$inserted}개 업소가 추가되었습니다. ({$skipped}개 중복 건너뜀)",
            'inserted' => $inserted, 'skipped' => $skipped, 'total' => count($businesses)
        ]);
    }
}'''

new_method = '''    // POST /api/admin/businesses/import - trigger server-side crawler or bulk import
    public function bulkImport(Request $req)
    {
        // Manual trigger from admin UI - run actual crawler on server
        if ($req->input('trigger') === 'manual') {
            $city = escapeshellarg($req->input('city', 'all'));
            $category = escapeshellarg($req->input('category', 'all'));
            $crawlerPath = base_path('crawler_server/crawler.py');

            // Kill any existing crawl
            exec('pkill -f crawler_server/crawler.py 2>/dev/null');
            // Clear old log
            file_put_contents('/tmp/crawl.log', '');
            // Write initial status
            file_put_contents('/tmp/crawl_status.json', json_encode([
                'status' => 'running', 'inserted' => 0, 'skipped' => 0,
                'progress' => '0/0', 'message' => 'Starting crawler...', 'updated_at' => now()
            ]));
            // Run crawler in background
            $cmd = "python3 {$crawlerPath} --city {$city} --category {$category} > /tmp/crawl.log 2>&1 &";
            exec($cmd);

            $total = DB::table('businesses')->count();
            return response()->json([
                'message' => "크롤링이 시작되었습니다!\\n도시: " . $req->input('city','전체') . "\\n카테고리: " . $req->input('category','전체') . "\\n\\n현재 업소 수: {$total}개\\n페이지를 새로고침하면 결과가 업데이트됩니다.",
                'status' => 'started', 'current_total' => $total
            ]);
        }

        // Check crawl status
        if ($req->input('action') === 'status') {
            $statusFile = '/tmp/crawl_status.json';
            if (file_exists($statusFile)) {
                $status = json_decode(file_get_contents($statusFile), true);
                $status['total_businesses'] = DB::table('businesses')->count();
                return response()->json($status);
            }
            return response()->json(['status' => 'idle', 'total_businesses' => DB::table('businesses')->count()]);
        }

        // Actual bulk import from crawler API call (array of businesses)
        $businesses = $req->input('businesses', []);
        if (empty($businesses)) {
            return response()->json(['message' => '가져올 업소 데이터가 없습니다.', 'inserted' => 0, 'skipped' => 0], 200);
        }
        $inserted = 0; $skipped = 0;
        foreach ($businesses as $biz) {
            $name = $biz['name_en'] ?? $biz['name_ko'] ?? $biz['name'] ?? '';
            if (!$name) { $skipped++; continue; }
            $exists = DB::table('businesses')->where('name', $name)->where('address', $biz['address'] ?? '')->exists();
            if ($exists) { $skipped++; continue; }
            DB::table('businesses')->insert([
                'name' => $name, 'name_ko' => $biz['name_ko'] ?? null, 'name_en' => $biz['name_en'] ?? null,
                'category' => $biz['category'] ?? '기타', 'address' => $biz['address'] ?? '',
                'phone' => $biz['phone'] ?? null, 'website' => $biz['website'] ?? null,
                'lat' => $biz['lat'] ?? null, 'lng' => $biz['lng'] ?? null,
                'region' => $biz['region'] ?? null, 'data_source' => 'crawler',
                'source_url' => $biz['source_url'] ?? null, 'status' => 'active',
                'is_active' => 1, 'created_at' => now(), 'updated_at' => now(),
            ]);
            $inserted++;
        }
        return response()->json([
            'message' => "{$inserted}개 업소가 추가되었습니다. ({$skipped}개 중복 건너뜀)",
            'inserted' => $inserted, 'skipped' => $skipped, 'total' => count($businesses)
        ]);
    }
}'''

if old_method in content:
    fixed = content.replace(old_method, new_method)
    print("\nUpdating AdminBusinessController...")
    print(write_file('/var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php', fixed))
    print(ssh('php -l /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php'))
else:
    print("ERROR: old_method pattern not found in controller")

# STEP 6: Add crawl status route to api.php
raw2 = ssh('base64 /var/www/somekorean/routes/api.php')
api_content = base64.b64decode(raw2).decode('utf-8')
# Add status route next to the existing import route
if "Route::post('businesses/import'" in api_content and "action.*status" not in api_content:
    api_fixed = api_content.replace(
        "Route::post('businesses/import', [AdminBusinessController::class, 'bulkImport']);",
        "Route::post('businesses/import', [AdminBusinessController::class, 'bulkImport']);\n    Route::get('businesses/crawl-status', [AdminBusinessController::class, 'bulkImport']);"
    )
    print("\nAdding crawl-status route...")
    print(write_file('/var/www/somekorean/routes/api.php', api_fixed))

print(ssh('cd /var/www/somekorean && php artisan route:clear && php artisan cache:clear 2>&1'))

print("\n=== Server crawler setup complete ===")
c.close()
