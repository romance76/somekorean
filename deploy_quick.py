import paramiko, os, sys
HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()
def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:100]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write(out.strip()[:500].encode('utf-8')); sys.stdout.buffer.write(b'\n')
    sys.stdout.buffer.flush()
def upload(rel):
    sftp.put(os.path.join(LOCAL, *rel.split('/')), f'{APP}/{rel}')
    sys.stdout.buffer.write(f'  UP: {rel.split("/")[-1]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

files = [
    'resources/js/pages/match/MatchHome.vue',
    'resources/js/pages/profile/UserDashboard.vue',
]
for f in files: upload(f)
run(f'cd {APP} && npm run build 2>&1 | tail -3', timeout=300)
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')
sftp.close(); client.close()
sys.stdout.buffer.write(b'DONE\n')
