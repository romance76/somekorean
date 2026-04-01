import paramiko, os, sys

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:120]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write(out.strip()[-500:].encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err and 'Deprec' not in err:
        sys.stdout.buffer.write(f'ERR: {err[:300]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

def upload_all():
    pages_dir = os.path.join(LOCAL, 'resources', 'js')
    count = 0
    for root, dirs, files in os.walk(pages_dir):
        for f in files:
            if f.endswith('.vue'):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, LOCAL).replace('\\', '/')
                remote = f'{APP}/{rel}'
                run(f'mkdir -p {os.path.dirname(remote)}')
                sftp.put(full, remote)
                count += 1
    sys.stdout.buffer.write(f'Uploaded {count} Vue files\n'.encode('utf-8')); sys.stdout.buffer.flush()

    # Also upload router
    sftp.put(os.path.join(LOCAL, 'resources', 'js', 'router', 'index.js'), f'{APP}/resources/js/router/index.js')
    sys.stdout.buffer.write(b'Uploaded router/index.js\n'); sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n=== MEGA DEPLOY ===\n'); sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n[1] Uploading all Vue files + router...\n'); sys.stdout.buffer.flush()
upload_all()

sys.stdout.buffer.write(b'\n[2] Building...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -5')

sys.stdout.buffer.write(b'\n[3] Check...\n'); sys.stdout.buffer.flush()
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== DONE ===\n'); sys.stdout.buffer.flush()
