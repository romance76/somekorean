import paramiko
import os

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"
OUT_DIR = "C:/Users/Admin/Desktop/somekorean/audit_files"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    return client

os.makedirs(OUT_DIR, exist_ok=True)
client = connect()

files = {
    "AdminLayout.vue": f"{APP}/resources/js/pages/admin/AdminLayout.vue",
    "AdminShorts.vue": f"{APP}/resources/js/pages/admin/AdminShorts.vue",
    "AdminRecipes.vue": f"{APP}/resources/js/pages/admin/AdminRecipes.vue",
    "Business.vue": f"{APP}/resources/js/pages/admin/Business.vue",
    "AdminController.php": f"{APP}/app/Http/Controllers/API/AdminController.php",
    "api.php": f"{APP}/routes/api.php",
    "router_index.js": f"{APP}/resources/js/router/index.js",
}

for name, path in files.items():
    out, err = ssh_cmd(client, f"cat {path}")
    dest = f"{OUT_DIR}/{name}"
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f"Saved {name}: {len(out)} chars")

client.close()
print("All files saved.")
