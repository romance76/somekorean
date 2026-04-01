import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e: time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-400:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-200:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local  = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

files = [
    # WebRTC 백엔드
    'app/Events/WebRTCSignal.php',
    'app/Http/Controllers/API/CallController.php',
    'routes/api.php',
    # WebRTC 프론트
    'resources/js/composables/useWebRTC.js',
    'resources/js/components/CallOverlay.vue',
    'resources/js/components/CallButton.vue',
    # i18n
    'resources/js/i18n/ko.js',
    'resources/js/i18n/en.js',
    'resources/js/stores/lang.js',
    # 업데이트
    'resources/js/components/NavBar.vue',
]

for f in files:
    upload(f)

# App.vue는 서버에 직접 작성 (Write tool이 없으므로)
app_vue = open(r'C:\Users\Admin\Desktop\somekorean\server_files\resources\js\App.vue', 'r', encoding='utf-8').read()
stdin, _, _ = client.exec_command(f'cat > {APP}/resources/js/App.vue', timeout=10)
stdin.write(app_vue)
stdin.channel.shutdown_write()
sys.stdout.buffer.write(b'UP: App.vue\n'); sys.stdout.buffer.flush()

# 빌드
run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write('\n=== Deploy Done ===\n'.encode('utf-8'))
sys.stdout.buffer.flush()
