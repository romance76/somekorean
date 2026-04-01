import paramiko, os, sys
HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()
def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:100]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write(out.strip()[-400:].encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err and 'Deprec' not in err:
        sys.stdout.buffer.write(f'ERR: {err[:300]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

sftp.put(os.path.join(LOCAL, 'app', 'Console', 'Commands', 'SeedEvents.php'), f'{APP}/app/Console/Commands/SeedEvents.php')
sys.stdout.buffer.write(b'UP: SeedEvents.php\n'); sys.stdout.buffer.flush()

run(f'cd {APP} && php artisan events:seed 2>&1')
run(f"cd {APP} && php artisan tinker --execute=\"echo 'Events: '.App\\\\Models\\\\Event::count();\"")
sftp.close(); client.close()
sys.stdout.buffer.write(b'DONE\n'); sys.stdout.buffer.flush()
