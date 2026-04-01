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

tests = [
    ("Q&A 카테고리", "curl -sk https://somekorean.com/api/qa/categories"),
    ("Q&A 목록", "curl -sk 'https://somekorean.com/api/qa?page=1'"),
    ("Q&A 상세 (1번)", "curl -sk https://somekorean.com/api/qa/1"),
    ("레시피 카테고리", "curl -sk https://somekorean.com/api/recipes/categories"),
    ("레시피 목록", "curl -sk 'https://somekorean.com/api/recipes?page=1'"),
    ("레시피 상세 (1번)", "curl -sk https://somekorean.com/api/recipes/1"),
    ("레시피 인기", "curl -sk https://somekorean.com/api/recipes/popular"),
]

for name, cmd in tests:
    out, err = ssh(cmd)
    if out.startswith('{') or out.startswith('['):
        # JSON response - show first 200 chars
        log(f"[OK] {name}: {out[:200]}")
    elif '500' in out or 'error' in out.lower() or '<html>' in out:
        log(f"[ERROR] {name}: {out[:200]}")
    else:
        log(f"[?] {name}: {out[:200]}")

c.close()
log("\nAll tests done!")
