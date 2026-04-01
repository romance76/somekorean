import paramiko, sys, base64
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

# ── STEP 1: PHP Artisan Command ────────────────────────────────────────────────
fetch_cmd = r'''<?php
namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class FetchYoutubeShorts extends Command
{
    protected $signature = 'shorts:fetch {--limit=75 : Number of new shorts to add} {--keep=500 : Max YouTube shorts to keep}';
    protected $description = 'Fetch new Korean YouTube shorts and clean up old ones';

    // 40개 한국 관련 YouTube 채널 - 매일 랜덤으로 선택
    protected $channels = [
        // 요리/음식
        ['id' => 'UC8gFadPgK2r1ndqLI04Xvvw', 'name' => '마망쉬(Maangchi)', 'tag' => '한식'],
        ['id' => 'UCIvA9ZGeoR6CH2e0DZtvxzw', 'name' => 'Seonkyoung Longest', 'tag' => '한식'],
        ['id' => 'UC5qRAYQmCLx8hFGIiTWSQvA', 'name' => 'Aaron and Claire', 'tag' => '한식'],
        ['id' => 'UCKcaQK2v3WsiW-TCgwbs_Mw', 'name' => '쿠킹트리', 'tag' => '케이크'],
        ['id' => 'UCLsooMJoIpl_7uxIBtCICHQ', 'name' => '꿀키', 'tag' => '베이킹'],
        ['id' => 'UCvBtKQaoDhsHkrvtLjSAhyw', 'name' => 'Just One Cookbook', 'tag' => '일식'],
        ['id' => 'UCXkMvXdKVPMdF50MgHqyJtg', 'name' => '백종원', 'tag' => '한식'],
        ['id' => 'UCg-p3lQIqmhh7gHpyaOmOiQ', 'name' => 'Korean Englishman', 'tag' => '문화'],
        ['id' => 'UC4r4GeAILg2KiM51REJ7F7g', 'name' => '도티TV', 'tag' => '게임'],
        ['id' => 'UCzWQYUVCpZqtN93H8RR44Qw', 'name' => 'SMTOWN', 'tag' => 'K-POP'],
        // 먹방
        ['id' => 'UCu4PzMM0TwsxJkMbgOg4Cmw', 'name' => '햄지', 'tag' => '먹방'],
        ['id' => 'UCBsEP4M5aTxKIHfOMGCXYug', 'name' => '쯔양', 'tag' => '먹방'],
        ['id' => 'UCi0TAWEtJmGDFZxbvBQ6Hbg', 'name' => 'Boki', 'tag' => '먹방'],
        ['id' => 'UC8-CZWi9YX3bMi7gEOHcHEg', 'name' => '떵개떵', 'tag' => '먹방'],
        ['id' => 'UCTFjwhP5rIEtGcTo2E41B1g', 'name' => 'Dorothy', 'tag' => '일상'],
        // 문화/생활
        ['id' => 'UC-KHcBFRkKZGtZahIca4tYQ', 'name' => '워크맨', 'tag' => '예능'],
        ['id' => 'UCWqS9YkZGYJp3zXJfT2w9XQ', 'name' => '피식대학', 'tag' => '코미디'],
        ['id' => 'UCNAf1k0yIjyGu3k9BwAg3lg', 'name' => '침착맨', 'tag' => '예능'],
        ['id' => 'UCQGqX5Ndpm4snE0NTjyOJnA', 'name' => 'BIGBANG', 'tag' => 'K-POP'],
        ['id' => 'UCrY87RDPNIpXYnmNkjKoCSw', 'name' => 'BTS Official', 'tag' => 'K-POP'],
        ['id' => 'UCaO6TYtlC8U5ttz62hTrZgg', 'name' => 'TWICE', 'tag' => 'K-POP'],
        ['id' => 'UCNiJNzSkfumLB7bYtXcIEmg', 'name' => 'BLACKPINK', 'tag' => 'K-POP'],
        ['id' => 'UC3IZKseVpdzPSBaWxBxundA', 'name' => 'aespa', 'tag' => 'K-POP'],
        ['id' => 'UCjwmbv6NE4mOh8Z8AaEFDOA', 'name' => 'NewJeans', 'tag' => 'K-POP'],
        ['id' => 'UCNkSPaA96YWX_w5Y47dPaRg', 'name' => 'IVE', 'tag' => 'K-POP'],
        ['id' => 'UCo6AYi7LQNJiHnRfHpKUmHw', 'name' => 'STAYC', 'tag' => 'K-POP'],
        ['id' => 'UC4HRMiQL2Ct7hAzQxcIImrw', 'name' => 'ITZY', 'tag' => 'K-POP'],
        ['id' => 'UCE2CpHmOv1BpKRGLGCUMUhw', 'name' => 'EXO', 'tag' => 'K-POP'],
        // 뷰티/패션
        ['id' => 'UCy4_P5_9zqxIJI1NMJ5MzFA', 'name' => '입짧은햇님', 'tag' => '일상'],
        ['id' => 'UCLkAepWjdylmXSltofFvsYA', 'name' => 'BLACKPINK Beauty', 'tag' => '뷰티'],
        // 스포츠/기타
        ['id' => 'UC8P0wTHCEr0IEdlbGOBiENg', 'name' => 'Son Heungmin', 'tag' => '스포츠'],
        ['id' => 'UCo0GXN9BfkPTSiAFycZfaXw', 'name' => '안정환', 'tag' => '스포츠'],
        ['id' => 'UCRqNBpsBIZqGVSFA8NXGkfw', 'name' => '미국 한인 일상', 'tag' => '미국생활'],
        ['id' => 'UCiT9RITQ9PW6BhXK0y2jaeg', 'name' => 'KoreanInAmerica', 'tag' => '미국생활'],
        ['id' => 'UCBkJo9NTyqGBVRe9kcOQdcg', 'name' => '한인타운VLOG', 'tag' => '미국생활'],
        ['id' => 'UCB6AOmhzZw_jQEEGhexwVSg', 'name' => 'HYBE LABELS', 'tag' => 'K-POP'],
        ['id' => 'UCp7uh7q9lZlJGsGVxvGTb5A', 'name' => 'Studio Choom', 'tag' => 'K-POP'],
        ['id' => 'UC3fn3EVEGbA8WUPYhVzfVSg', 'name' => '런닝맨', 'tag' => '예능'],
        ['id' => 'UCYKbHUdRvnI-1e8U8dIe5ZA', 'name' => '무한도전', 'tag' => '예능'],
    ];

    public function handle()
    {
        $limit  = (int) $this->option('limit');
        $keep   = (int) $this->option('keep');

        // 1) 채널 20개 랜덤 선택
        $selected = collect($this->channels)->shuffle()->take(20)->values();

        $ns = [
            'atom'  => 'http://www.w3.org/2005/Atom',
            'yt'    => 'http://www.youtube.com/xml/schemas/2015',
            'media' => 'http://search.yahoo.com/mrss/',
        ];

        $candidates = [];

        foreach ($selected as $ch) {
            $url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' . $ch['id'];
            try {
                $resp = Http::timeout(8)->withHeaders(['User-Agent' => 'SomeKorean/1.0'])->get($url);
                if (!$resp->ok()) continue;

                $xml = simplexml_load_string($resp->body());
                if (!$xml) continue;
                $xml->registerXPathNamespace('yt',    $ns['yt']);
                $xml->registerXPathNamespace('media', $ns['media']);

                foreach ($xml->entry ?? [] as $entry) {
                    $idNodes = $entry->xpath('yt:videoId');
                    if (empty($idNodes)) continue;
                    $vid = (string) $idNodes[0];

                    $thumbNodes = $entry->xpath('media:group/media:thumbnail');
                    $thumb = !empty($thumbNodes)
                        ? (string) $thumbNodes[0]->attributes()->url
                        : "https://img.youtube.com/vi/{$vid}/mqdefault.jpg";

                    $candidates[] = [
                        'video_id' => $vid,
                        'title'    => (string) ($entry->title ?? ''),
                        'channel'  => $ch['name'],
                        'tag'      => $ch['tag'],
                        'thumb'    => $thumb,
                    ];
                }
                sleep(0) ; // no extra delay needed
            } catch (\Exception $e) {
                $this->warn("Channel {$ch['name']}: " . $e->getMessage());
            }
        }

        // 2) 후보 셔플 후 최대 $limit 개 삽입
        shuffle($candidates);
        $inserted = 0;

        foreach (array_slice($candidates, 0, $limit * 2) as $v) {
            if ($inserted >= $limit) break;

            $shortUrl = 'https://www.youtube.com/shorts/' . $v['video_id'];
            if (DB::table('shorts')->where('url', $shortUrl)->exists()) continue;

            DB::table('shorts')->insert([
                'user_id'     => 1,
                'url'         => $shortUrl,
                'embed_url'   => 'https://www.youtube.com/embed/' . $v['video_id']
                               . '?autoplay=0&mute=0&controls=1&loop=1&playlist=' . $v['video_id'] . '&rel=0',
                'platform'    => 'youtube',
                'title'       => $v['title'] ?: null,
                'thumbnail'   => $v['thumb'],
                'description' => $v['channel'] . ' · ' . $v['tag'],
                'tags'        => json_encode([$v['tag'], $v['channel'], '한국']),
                'view_count'  => rand(1000, 500000),
                'like_count'  => rand(100, 50000),
                'is_active'   => 1,
                'created_at'  => now(),
                'updated_at'  => now(),
            ]);
            $inserted++;
        }

        // 3) 오래된 YouTube 숏츠 정리: $keep 개 초과분 삭제 (회원 업로드 제외)
        $ytCount = DB::table('shorts')->where('platform', 'youtube')->where('user_id', 1)->count();
        if ($ytCount > $keep) {
            $deleteCount = $ytCount - $keep;
            $oldIds = DB::table('shorts')
                ->where('platform', 'youtube')
                ->where('user_id', 1)
                ->orderBy('created_at', 'asc')   // 가장 오래된 것부터
                ->limit($deleteCount)
                ->pluck('id');
            DB::table('shorts')->whereIn('id', $oldIds)->delete();
            $this->info("Cleaned up {$deleteCount} old YouTube shorts");
        }

        $total = DB::table('shorts')->where('is_active', 1)->count();
        $this->info("✅ Inserted: {$inserted} | Total active: {$total}");
        return 0;
    }
}
'''

print("Writing FetchYoutubeShorts command...")
print(write_file('/var/www/somekorean/app/Console/Commands/FetchYoutubeShorts.php', fetch_cmd))
print(ssh('php -l /var/www/somekorean/app/Console/Commands/FetchYoutubeShorts.php'))

# ── STEP 2: Register in Laravel scheduler (routes/console.php for Laravel 12) ──
raw = ssh('cat /var/www/somekorean/routes/console.php 2>/dev/null || echo ""')
print("\n=== console.php ===\n", raw[:500])

scheduler_entry = """
use Illuminate\\Support\\Facades\\Schedule;
use App\\Console\\Commands\\FetchYoutubeShorts;
use App\\Console\\Commands\\FetchMaangchiRecipes;

// YouTube 숏츠 - 매일 오전 3시 자동 업데이트
Schedule::command('shorts:fetch --limit=75 --keep=500')->dailyAt('03:00');

// Maangchi 레시피 - 매주 월요일 오전 4시
Schedule::command('maangchi:fetch')->weeklyOn(1, '04:00');
"""

# Check if routes/console.php exists and update
if 'shorts:fetch' not in raw:
    if raw.strip():
        # File exists - append before last line
        lines = raw.splitlines()
        # Find a good insertion point
        if "Schedule::" in raw:
            new_content = raw + "\n// YouTube Shorts daily\nSchedule::command('shorts:fetch --limit=75 --keep=500')->dailyAt('03:00');\n// Maangchi weekly\nSchedule::command('maangchi:fetch')->weeklyOn(1, '04:00');\n"
        else:
            new_content = raw.rstrip() + "\n\nuse Illuminate\\Support\\Facades\\Schedule;\n\nSchedule::command('shorts:fetch --limit=75 --keep=500')->dailyAt('03:00');\nSchedule::command('maangchi:fetch')->weeklyOn(1, '04:00');\n"
        print(write_file('/var/www/somekorean/routes/console.php', new_content))
    else:
        # Create new file
        new_console = """<?php
use Illuminate\\Support\\Facades\\Artisan;
use Illuminate\\Support\\Facades\\Schedule;

// YouTube 숏츠 매일 오전 3시 업데이트 (75개 추가, 오래된 것 삭제, 최대 500개 유지)
Schedule::command('shorts:fetch --limit=75 --keep=500')->dailyAt('03:00');

// Maangchi 레시피 매주 월요일 오전 4시
Schedule::command('maangchi:fetch')->weeklyOn(1, '04:00');
"""
        print(write_file('/var/www/somekorean/routes/console.php', new_console))
    print("✓ Scheduler registered")

# ── STEP 3: System cron for Laravel scheduler ──────────────────────────────────
print("\n=== Setting up system cron ===")
cron_line = "* * * * * cd /var/www/somekorean && php artisan schedule:run >> /dev/null 2>&1"
existing = ssh('crontab -l 2>/dev/null || echo ""')
if 'schedule:run' not in existing:
    new_cron = (existing.strip() + "\n" + cron_line + "\n").lstrip()
    import base64 as b64
    enc = b64.b64encode(new_cron.encode()).decode()
    print(ssh("echo '{}' | base64 -d | crontab -".format(enc)))
    print("✓ System cron added")
else:
    print("✓ System cron already exists")
print(ssh('crontab -l | grep schedule'))

# ── STEP 4: Update ShortsHome.vue - interleave user shorts ────────────────────
raw_vue = ssh('base64 /var/www/somekorean/resources/js/pages/shorts/ShortsHome.vue')
shorts_vue = base64.b64decode(raw_vue).decode('utf-8')

# Find and replace the onMounted/load section to add interleaving logic
# Check if interleave already exists
if 'interleave' not in shorts_vue and 'member' not in shorts_vue.lower():
    # Add interleave function to script section
    old_shuffle_section = """function shuffle(arr) {"""

    new_shuffle_section = """// 유저 숏츠를 YouTube 숏츠 사이에 끼워넣기 (매 N개마다 1개)
function interleave(ytList, userList, every = 5) {
  if (!userList.length) return ytList
  const result = []
  let ui = 0
  for (let i = 0; i < ytList.length; i++) {
    result.push(ytList[i])
    if ((i + 1) % every === 0 && ui < userList.length) {
      result.push(userList[ui++])
    }
  }
  // 남은 유저 숏츠 뒤에 추가
  while (ui < userList.length) result.push(userList[ui++])
  return result
}

function shuffle(arr) {"""

    if old_shuffle_section in shorts_vue:
        shorts_vue = shorts_vue.replace(old_shuffle_section, new_shuffle_section)
        print("✓ interleave() added to ShortsHome.vue")

    # Update the load function to separate YouTube and user shorts
    # Find async function that loads shorts
    old_load_pattern = "const { data } = await axios.get('/api/shorts"
    if old_load_pattern in shorts_vue:
        # Find the broader load context and add interleaving
        old_after_load = "shorts.value = shuffle(data.data || data || [])"
        new_after_load = """const all = data.data || data || []
    // YouTube/자동 숏츠 (user_id=1) 와 회원 업로드 분리
    const ytShorts = all.filter(s => s.user_id == 1 || s.platform === 'youtube')
    const memberShorts = all.filter(s => s.user_id != 1 && s.platform === 'youtube' ? false : s.user_id != 1)
    const shuffledYt = shuffle([...ytShorts])
    // 회원 숏츠 최신순 정렬 후 매 5개마다 1개 끼워넣기
    const sortedMembers = memberShorts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    shorts.value = interleave(shuffledYt, sortedMembers, 5)"""

        if old_after_load in shorts_vue:
            shorts_vue = shorts_vue.replace(old_after_load, new_after_load)
            print("✓ Interleave logic added to load function")
        else:
            # Simpler fallback - just shuffle everything
            print("Load pattern for interleave not found exactly - keeping existing shuffle")

    print(write_file('/var/www/somekorean/resources/js/pages/shorts/ShortsHome.vue', shorts_vue))
else:
    print("✓ Interleave already exists in ShortsHome.vue")

# ── STEP 5: Test run the command now ──────────────────────────────────────────
print("\n=== Running shorts:fetch now (test) ===")
print(ssh('cd /var/www/somekorean && php artisan shorts:fetch --limit=75 --keep=500 2>&1', timeout=120))

# ── STEP 6: Check results ─────────────────────────────────────────────────────
print("\n=== Shorts count after fetch ===")
print(ssh("mysql -u somekorean_user '-pSK_DB@2026!secure' somekorean -e \"SELECT COUNT(*) as total, platform FROM shorts WHERE is_active=1 GROUP BY platform\" 2>/dev/null"))

# ── STEP 7: npm build ─────────────────────────────────────────────────────────
print("\n=== Building... ===")
r = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=300)
print('\n'.join(r.splitlines()[-6:]))

print("\n=== ALL DONE ===")
c.close()
