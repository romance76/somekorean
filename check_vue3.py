import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:70]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR]{err[:200]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

run(f'cat {APP}/resources/js/bootstrap.js')
run(f'cat {APP}/resources/js/app.js')
run(f'cat {APP}/resources/js/pages/auth/Login.vue')
run(f'wc -l {APP}/resources/js/pages/community/PostDetail.vue {APP}/resources/js/pages/jobs/JobList.vue {APP}/resources/js/pages/market/MarketList.vue')

client.close()
print('\nDONE')
