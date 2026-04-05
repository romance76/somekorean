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

# Get laravel log errors
out, _ = ssh("tail -100 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -A5 'ERROR\\|Exception\\|Error' | tail -50")
log("Laravel errors:\n" + out)

# Test individual API calls with verbose output
out, _ = ssh("curl -sk 'https://somekorean.com/api/qa?page=1' 2>&1")
log("\nQ&A list raw response:\n" + out[:2000])

c.close()
