import paramiko, sys

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=300):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

print("Running build...")
out, err = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -30", timeout=300)
sys.stdout.buffer.write(("BUILD OUTPUT:\n" + out + "\n").encode('utf-8'))
if err:
    sys.stdout.buffer.write(("STDERR: " + err + "\n").encode('utf-8'))

print("\nClearing caches...")
out2, err2 = ssh("cd /var/www/somekorean && php artisan config:clear && php artisan route:clear && php artisan view:clear")
sys.stdout.buffer.write(("CACHE CLEAR:\n" + out2 + "\n").encode('utf-8'))
