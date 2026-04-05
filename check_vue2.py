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

run(f'cat {APP}/resources/js/pages/Home.vue')
run(f'cat {APP}/resources/js/pages/community/PostList.vue')
run(f'cat {APP}/resources/js/router/index.js')
run(f'cat {APP}/resources/js/stores/auth.js')

client.close()
print('\nDONE')
