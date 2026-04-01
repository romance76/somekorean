#!/usr/bin/env python3
import paramiko, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=30):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip(), stderr.read().decode('utf-8', errors='replace').strip()

# Check latest error
out, _ = ssh("tail -50 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -A3 'ERROR\\|CRITICAL' | tail -20")
log("Latest errors:\n" + out)

# Try recipe detail
out, _ = ssh("curl -sk https://somekorean.com/api/recipes/1 2>&1 | python3 -c \"import sys; html=sys.stdin.read(); print(html[-500:] if len(html)>500 else html)\"")
log("\nRecipe detail response end:\n" + out[:500])

c.close()
