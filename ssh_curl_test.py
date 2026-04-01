import paramiko

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

# Test the admin shorts endpoint
print("=== Test: GET /api/admin/shorts (no auth) ===")
out, err = ssh_cmd(client, 'curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer test_invalid" http://localhost/api/admin/shorts')
print(f"HTTP status: {out.strip()}")

print("\n=== Test: GET /api/admin/shorts response body ===")
out, err = ssh_cmd(client, 'curl -s -H "Authorization: Bearer test_invalid" http://localhost/api/admin/shorts | head -c 200')
print(out)

# Check AdminRecipeController exists
print("\n=== Check AdminRecipeController exists ===")
out, err = ssh_cmd(client, 'ls -la /var/www/somekorean/app/Http/Controllers/API/AdminRecipeController.php 2>&1')
print(out.strip())

# Check AdminBusinessController exists
print("\n=== Check AdminBusinessController exists ===")
out, err = ssh_cmd(client, 'ls -la /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php 2>&1')
print(out.strip())

# Check for duplicate routes in router/index.js
print("\n=== Check duplicate routes ===")
out, err = ssh_cmd(client, "grep -n \"path: '/games/tower-defense'\" /var/www/somekorean/resources/js/router/index.js")
print("tower-defense duplicates:", out.strip())

out, err = ssh_cmd(client, "grep -n \"path: '/games/stroop'\" /var/www/somekorean/resources/js/router/index.js")
print("stroop duplicates:", out.strip())

# Check route indentation issue at line 554 (missing indentation)
print("\n=== api.php line 553-556 context ===")
out, err = ssh_cmd(client, "sed -n '550,558p' /var/www/somekorean/routes/api.php")
print(out)

client.close()
print("=== DONE ===")
