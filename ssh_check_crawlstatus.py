import paramiko

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

# Check current state of api.php crawl-status
print("=== api.php crawl-status route ===")
out, _ = ssh_cmd(client, f"grep -n 'crawl' {APP}/routes/api.php")
print(out)

# Check AdminBusinessController has crawlStatus or bulkImport
print("=== AdminBusinessController - check crawlStatus ===")
out, _ = ssh_cmd(client, f"grep -n 'crawlStatus\|bulkImport\|function' {APP}/app/Http/Controllers/API/AdminBusinessController.php | tail -20")
print(out)

# Check AdminController getShorts fix was applied
print("=== AdminController - verify getShorts fix ===")
out, _ = ssh_cmd(client, f"grep -A5 'platform' {APP}/app/Http/Controllers/API/AdminController.php | head -20")
print(out)

# Now build the frontend to apply changes
print("=== Check if npm/yarn available ===")
out, _ = ssh_cmd(client, "which npm && npm --version 2>&1 | head -2")
print(out.strip())

out, _ = ssh_cmd(client, "ls /var/www/somekorean/package.json 2>/dev/null | head -1")
print("package.json:", out.strip())

client.close()
print("=== DONE ===")
