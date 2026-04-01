import paramiko, os, sys
HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()
def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'{out.strip()[:300]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

sftp.put(os.path.join(LOCAL, 'app', 'Http', 'Controllers', 'API', 'ClubController.php'), f'{APP}/app/Http/Controllers/API/ClubController.php')
sys.stdout.buffer.write(b'UP: ClubController.php\n'); sys.stdout.buffer.flush()

# Make sure storage link exists for public uploads
run(f'cd {APP} && php artisan storage:link 2>&1 || true')
run(f'mkdir -p {APP}/storage/app/public/clubs')

sftp.close(); client.close()
sys.stdout.buffer.write(b'DONE\n'); sys.stdout.buffer.flush()
