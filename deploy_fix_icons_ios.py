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
    # 아이콘 중복 수정: i18n에서 이모지 제거
    'resources/js/i18n/ko.js',
    'resources/js/i18n/en.js',
    # iOS 줌 버그 수정: ChatRooms CSS (calc 방식, text-base)
    'resources/js/pages/chat/ChatRooms.vue',
    # iOS 글로벌 CSS: 모든 input 16px 강제
    'resources/css/app.css',
]

for f in files:
    upload(f)

run(f'cd {APP} && npm run build 2>&1 | tail -6', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write('\n=== Done ===\n'.encode('utf-8'))
sys.stdout.buffer.flush()
