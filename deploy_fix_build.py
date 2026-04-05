import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=20)
sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-800:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    if not os.path.exists(local):
        sys.stdout.buffer.write(f'SKIP: {rel}\n'.encode('utf-8'))
        return
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

# 수정된 파일들 업로드
upload('resources/js/router/index.js')        # 임시 fallback import
upload('database/seeders/AdminDummyDataSeeder.php')  # FK 수정

# 시더 재실행
run(f'cd {APP} && php8.2 artisan db:seed --class=AdminDummyDataSeeder --force 2>&1 | tail -5')

# 빌드
run(f'cd {APP} && npm run build 2>&1 | tail -6', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== Fix Done ===\n')
sys.stdout.buffer.flush()
