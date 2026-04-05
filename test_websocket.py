import paramiko
import json
import requests

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

print("="*60)
print("=== WEBSOCKET & SERVER CHECKS ===")
print("="*60)

# 1. Check port 8080
print("\n[1] Port 8080 Status")
out, err = run("ss -tlnp | grep 8080 || netstat -tlnp 2>/dev/null | grep 8080")
print(f"  Port 8080: {out.strip() or 'NOT LISTENING'}")

# 2. Check WebSocket server process
print("\n[2] WebSocket Server Process")
out, err = run("ps aux | grep -E 'reverb|soketi|laravel|artisan' | grep -v grep")
print(f"  Processes: {out.strip() or 'NONE'}")

# 3. Check nginx config for /app proxy
print("\n[3] Nginx /app proxy config")
out, err = run("grep -r 'app\|8080\|websocket\|ws' /etc/nginx/sites-enabled/ 2>/dev/null | head -30")
print(f"  Nginx WS config:\n{out[:1000]}")

# 4. Check Laravel Reverb configuration
print("\n[4] Laravel Reverb/Broadcasting config")
out, err = run("cat /var/www/somekorean/.env | grep -E 'BROADCAST|REVERB|PUSHER|SOKETI|WS' 2>/dev/null")
print(f"  Env vars: {out.strip()}")

# 5. Check if Reverb is installed
out, err = run("cd /var/www/somekorean && composer show | grep -E 'reverb|soketi|pusher' 2>/dev/null | head -10")
print(f"\n[5] WS Packages: {out.strip() or 'NONE'}")

# 6. Check broadcasting channels
out, err = run("cat /var/www/somekorean/routes/channels.php 2>/dev/null")
print(f"\n[6] Channels.php:\n{out[:1000]}")

# 7. Check if reverb service file exists
out, err = run("ls /etc/systemd/system/ | grep -E 'reverb|soketi|websocket'")
print(f"\n[7] Systemd services: {out.strip() or 'NONE'}")

# 8. Try to start reverb
print("\n[8] Try starting Laravel Reverb")
out, err = run("cd /var/www/somekorean && php artisan reverb:start --port=8080 --daemon 2>&1 &")
print(f"  Start result: {out[:200]} {err[:200]}")

import time
time.sleep(3)

# 9. Check again
out, err = run("ss -tlnp | grep 8080 || netstat -tlnp 2>/dev/null | grep 8080")
print(f"\n[9] Port 8080 after start: {out.strip() or 'NOT LISTENING'}")

# 10. Check reverb process
out, err = run("ps aux | grep reverb | grep -v grep")
print(f"\n[10] Reverb process: {out.strip() or 'NONE'}")

# 11. Check full nginx config
print("\n[11] Full Nginx Config")
out, err = run("cat /etc/nginx/sites-enabled/somekorean 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null | head -100")
print(out[:2000])

client.close()
