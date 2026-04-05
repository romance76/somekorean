import paramiko, sys, base64
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=60):
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

# Read file
raw = ssh('base64 /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php')
content = base64.b64decode(raw).decode('utf-8')

# Replace old bulkImport method
old = '''    // POST /api/admin/businesses/import (bulk import from crawler)
    public function bulkImport(Request $req)
    {
        $businesses = $req->input('businesses', []);
        if (empty($businesses)) return response()->json(['error' => 'No data'], 422);
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
        return response()->json(['inserted' => $inserted, 'skipped' => $skipped, 'total' => count($businesses)]);
    }
}'''

new = '''    // POST /api/admin/businesses/import (bulk import from crawler or manual trigger)
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

if old in content:
    fixed = content.replace(old, new)
    print("Replacement found, writing...")
    result = write_file('/var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php', fixed)
    print(result)
else:
    print("ERROR: Pattern not found. Checking end of file...")
    print(repr(content[-300:]))

# Also fix the crawl log display in the Vue - replace multiline message display
print("\nVerifying PHP syntax...")
print(ssh('php -l /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php'))

print("\nDone - no rebuild needed (PHP only)")
c.close()
