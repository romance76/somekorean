import paramiko
import os
import sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:80]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Chat Fix + BottomNav Update ===')

# 1. Upload app.js (Echo initialization)
print('\n[1] Uploading app.js with Echo init...')
upload(os.path.join(LOCAL,'resources','js','app.js'),
       f'{APP}/resources/js/app.js')

# 2. Upload BottomNav
print('\n[2] Uploading BottomNav.vue...')
upload(os.path.join(LOCAL,'resources','js','components','BottomNav.vue'),
       f'{APP}/resources/js/components/BottomNav.vue')

# 3. Check broadcasting config
print('\n[3] Checking broadcast config...')
run(f'cd {APP} && grep -E "BROADCAST|REVERB" .env | head -20')

# 4. Make sure BroadcastServiceProvider is enabled
print('\n[4] Checking BroadcastServiceProvider...')
run(f'grep -r "BroadcastServiceProvider" {APP}/bootstrap/providers.php 2>/dev/null || echo "not in providers"')
run(f'grep -r "Broadcast" {APP}/config/app.php 2>/dev/null | head -5')

# 5. Make sure broadcasting routes are loaded
print('\n[5] Checking routes/channels.php...')
run(f'ls {APP}/routes/channels.php && cat {APP}/routes/channels.php')

# 6. Rebuild
print('\n[6] Rebuilding frontend...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# 7. Final check
print('\n[7] Final check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Chat Fix DONE ===')
