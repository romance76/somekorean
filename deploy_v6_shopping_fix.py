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

def run(cmd, timeout=120):
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
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n=== [V6 Fix] Shopping Deals Schema Fix ===\n')
sys.stdout.buffer.flush()

upload('database/migrations/2026_03_29_000011_recreate_shopping_deals_table.php')

run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -5')

sys.stdout.buffer.write(b'\n=== Fetching Shopping Deals ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan shopping:fetch 2>&1 | tail -15', timeout=60)

sys.stdout.buffer.write(b'\n=== Shopping Fix DONE ===\n')
sys.stdout.buffer.flush()

sftp.close(); client.close()
