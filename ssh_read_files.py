import paramiko

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    return client

client = connect()

files = {
    "AdminLayout": f"{APP}/resources/js/pages/admin/AdminLayout.vue",
    "AdminShorts": f"{APP}/resources/js/pages/admin/AdminShorts.vue",
    "AdminRecipes": f"{APP}/resources/js/pages/admin/AdminRecipes.vue",
    "Business": f"{APP}/resources/js/pages/admin/Business.vue",
    "AdminController": f"{APP}/app/Http/Controllers/API/AdminController.php",
    "api_php": f"{APP}/routes/api.php",
    "router": f"{APP}/resources/js/router/index.js",
}

for name, path in files.items():
    out, err = ssh_cmd(client, f"wc -l {path} 2>/dev/null && echo '---EXISTS---'")
    print(f"\n{'='*60}")
    print(f"FILE: {name} => {path}")
    print(f"SIZE: {out.strip()}")

client.close()
