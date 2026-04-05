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

# curl via HTTPS (SSL) with -k to ignore cert
print("=== Test: HTTPS /api/admin/shorts (401 expected) ===")
out, err = ssh_cmd(client, 'curl -sk -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid_token" https://somekorean.com/api/admin/shorts')
print(f"HTTP status: {out.strip()}")

out, err = ssh_cmd(client, 'curl -sk -H "Authorization: Bearer invalid_token" https://somekorean.com/api/admin/shorts | head -c 300')
print(f"Response: {out.strip()}")

# Check for getShorts filter by platform (not implemented in getShorts!)
print("\n=== Check getShorts for platform/status filter ===")
out, err = ssh_cmd(client, "sed -n '523,537p' /var/www/somekorean/app/Http/Controllers/API/AdminController.php")
print(out)

# Check AdminRecipeController methods
print("\n=== AdminRecipeController methods ===")
out, err = ssh_cmd(client, "grep 'public function' /var/www/somekorean/app/Http/Controllers/API/AdminRecipeController.php")
print(out)

# Check AdminBusinessController methods
print("\n=== AdminBusinessController methods ===")
out, err = ssh_cmd(client, "grep 'public function' /var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php")
print(out)

# Check duplicate routes in router/index.js more thoroughly
print("\n=== All duplicate route names in router/index.js ===")
out, err = ssh_cmd(client, "grep -oP \"name: '.*?'\" /var/www/somekorean/resources/js/router/index.js | sort | uniq -d")
print("Duplicate names:", out.strip())

out, err = ssh_cmd(client, "grep -oP \"path: '.*?'\" /var/www/somekorean/resources/js/router/index.js | sort | uniq -d")
print("Duplicate paths:", out.strip())

# Check api.php line 554 indentation issue
print("\n=== api.php crawl-status route indentation issue ===")
out, err = ssh_cmd(client, "sed -n '540,560p' /var/www/somekorean/routes/api.php")
print(out)

client.close()
print("=== DONE ===")
