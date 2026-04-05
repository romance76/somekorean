import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=300):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    result = out.read().decode('utf-8', errors='replace').strip()
    error = err.read().decode('utf-8', errors='replace').strip()
    return result, error

print("Running npm build...")
out, err = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -10", timeout=300)
print(out)
if err:
    print("STDERR:", err)

print("\nRunning artisan route:cache...")
out, err = ssh("cd /var/www/somekorean && php artisan route:cache 2>&1 | tail -2")
print(out)
if err:
    print("STDERR:", err)

c.close()
print("\n=== Build complete ===")
