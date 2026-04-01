import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for attempt in range(3):
    try:
        client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e:
        sys.stdout.buffer.write(f'retry {attempt+1}: {e}\n'.encode('utf-8')); sys.stdout.buffer.flush()
        time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-500:] + '\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: ' + err.strip()[-200:] + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def mkdir_remote(path):
    run(f'mkdir -p {path}')

def upload(rel):
    local  = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    mkdir_remote(remote.rsplit('/', 1)[0])
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

files = [
    'app/Http/Controllers/API/AIController.php',
    'app/Http/Controllers/API/GroupBuyController.php',
    'app/Http/Controllers/API/MentorController.php',
    'app/Models/GroupBuy.php',
    'app/Models/GroupBuyParticipant.php',
    'app/Models/Mentor.php',
    'app/Models/MentorRequest.php',
    'app/Console/Commands/FetchNews.php',
    'database/migrations/2026_03_28_300000_phase5_features.php',
    'routes/api.php',
    'resources/js/pages/ai/AISearch.vue',
    'resources/js/pages/groupbuy/GroupBuyHome.vue',
    'resources/js/pages/mentor/MentorHome.vue',
    'resources/js/router/index.js',
    'resources/js/components/NavBar.vue',
]

for f in files:
    upload(f)

# OpenAI 키 .env 추가 (없을 때만)
run(f"grep -q 'OPENAI_API_KEY' {APP}/.env || echo 'OPENAI_API_KEY=' >> {APP}/.env")

# services.php openai 설정 추가 (없을 때만)
run(f"""php -r "
\\$f = file_get_contents('{APP}/config/services.php');
if (strpos(\\$f, 'openai') === false) {{
    \\$f = str_replace('];', \\"    'openai' => ['key' => env('OPENAI_API_KEY', '')],\\n];\\", \\$f);
    file_put_contents('{APP}/config/services.php', \\$f);
    echo 'openai config added';
}} else {{ echo 'openai config exists'; }}" """)

# 마이그레이션
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1')

# 뉴스봇 crontab (3시간마다)
run("(crontab -l 2>/dev/null | grep -v 'news:fetch'; echo '0 */3 * * * cd /var/www/somekorean && php8.2 artisan news:fetch >> /var/log/news_fetch.log 2>&1') | crontab -")

# 빌드
run(f'cd {APP} && npm run build 2>&1 | tail -4', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== Phase 5 Deploy Done ===\n'); sys.stdout.buffer.flush()
