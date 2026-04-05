import paramiko
import re

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

out, _ = ssh_cmd(client, f"cat {APP}/resources/js/router/index.js")

# Find remaining duplicates with context
print("=== Remaining duplicate analysis ===")
# Find all /games/bingo lines
for i, line in enumerate(out.split('\n'), 1):
    if "'/games/bingo'" in line or "'/games/memory'" in line or "name: 'home'" in line or "name: 'login'" in line:
        print(f"Line {i}: {line.strip()}")

client.close()
