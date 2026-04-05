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

# Test HTTPS
out, _ = ssh("curl -sk https://somekorean.com/api/qa/categories 2>&1 | head -500")
log("HTTPS Q&A categories:\n" + out[:800])

out, _ = ssh("curl -sk https://somekorean.com/api/recipes/categories 2>&1 | head -500")
log("\nHTTPS Recipe categories:\n" + out[:800])

out, _ = ssh("curl -sk 'https://somekorean.com/api/qa?page=1' 2>&1 | head -200")
log("\nHTTPS Q&A list:\n" + out[:500])

c.close()
log("Done!")
