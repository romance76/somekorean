import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Get full routes
out, err = run('cd /var/www/somekorean && php artisan route:list --path=chat 2>&1')
print("=== CHAT ROUTES ===")
print(out[:3000])

out, err = run('cd /var/www/somekorean && php artisan route:list --path=match 2>&1')
print("\n=== MATCH ROUTES ===")
print(out[:3000])

out, err = run('cd /var/www/somekorean && php artisan route:list --path=friend 2>&1')
print("\n=== FRIEND ROUTES ===")
print(out[:3000])

# Also check full api.php for chat/match/friend sections
out, err = run("grep -n 'chat\|match\|friend' /var/www/somekorean/routes/api.php | head -80")
print("\n=== ROUTES grep ===")
print(out)

client.close()
