import paramiko
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f'>>> {cmd[:100]}')
    if out: print(out[:1500])
    if err and 'Warning' not in err: print(f'ERR: {err[:500]}')
    print()

APP = '/var/www/somekorean'

# Get token for user 1
run(f"cd {APP} && php artisan tinker --execute=\"\\$u = App\\\\Models\\\\User::first(); echo auth('api')->login(\\$u);\"")

# Call browse API with token
token_cmd = f"cd {APP} && php artisan tinker --execute=\"\\$u = App\\\\Models\\\\User::first(); echo auth('api')->login(\\$u);\""
stdin, stdout, stderr = client.exec_command(token_cmd, timeout=30)
token = stdout.read().decode('utf-8', errors='replace').strip()
print(f'Token: {token[:30]}...')

# Test the API
run(f"curl -s 'https://somekorean.com/api/match/browse' -H 'Authorization: Bearer {token}' | head -500")
run(f"curl -s 'https://somekorean.com/api/match/browse' -H 'Authorization: Bearer {token}' -w '\\nHTTP_CODE:%{{http_code}}' -o /tmp/match_out.json && cat /tmp/match_out.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f\"Count: {{len(d)}}\"); [print(f\"  {{p.get(\\\"nickname\\\")}} age={{p.get(\\\"age\\\")}}\") for p in d[:3]]'")

# Check laravel log for recent browse errors
run(f"grep -i 'match\\|browse\\|error' {APP}/storage/logs/laravel.log 2>/dev/null | tail -10")

client.close()
