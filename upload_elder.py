import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

local_path = r'C:\Users\Admin\Desktop\somekorean\Elder.vue'
remote_path = '/var/www/somekorean/resources/js/pages/admin/Elder.vue'

with open(local_path, 'rb') as f:
    content = f.read()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

# Use stdin to pipe content
cmd = 'cat > ' + remote_path
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
stdin.write(content)
stdin.channel.shutdown_write()
exit_code = stdout.channel.recv_exit_status()
err = stderr.read().decode('utf-8', errors='replace')
if exit_code != 0:
    print(f'Error: {err}', file=sys.stderr)
    sys.exit(1)

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command('wc -c ' + remote_path, timeout=10)
print(stdout2.read().decode('utf-8', errors='replace').strip())

ssh.close()
print(f'Uploaded {len(content)} bytes')
