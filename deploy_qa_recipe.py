import sys
import os
import paramiko

def out(msg):
    sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
    sys.stdout.buffer.flush()

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
REMOTE_BASE = "/var/www/somekorean"
LOCAL_BASE = r"C:\Users\Admin\Desktop\somekorean\server_files"

FILES = [
    "app/Models/QaCategory.php",
    "app/Models/QaPost.php",
    "app/Models/QaAnswer.php",
    "app/Models/RecipeCategory.php",
    "app/Models/RecipePost.php",
    "app/Models/RecipeComment.php",
    "app/Http/Controllers/API/QaController.php",
    "app/Http/Controllers/API/RecipeController.php",
    "app/Http/Controllers/API/AdminQaController.php",
    "app/Http/Controllers/API/AdminRecipeController.php",
    "database/migrations/2026_03_29_000030_create_qa_tables.php",
    "database/migrations/2026_03_29_000031_create_recipe_tables.php",
    "routes/api.php",
    "resources/js/router/index.js",
    "resources/js/components/NavBar.vue",
    "resources/js/pages/admin/AdminLayout.vue",
    "resources/js/pages/admin/AdminQa.vue",
    "resources/js/pages/admin/AdminRecipes.vue",
    "resources/js/pages/admin/Chats.vue",
    "resources/js/pages/qa/QaList.vue",
    "resources/js/pages/qa/QaDetail.vue",
    "resources/js/pages/recipes/RecipeList.vue",
    "resources/js/pages/recipes/RecipeDetail.vue",
]

def run_cmd(ssh, cmd):
    out(f"  $ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out_data = stdout.read().decode('utf-8', errors='replace')
    err_data = stderr.read().decode('utf-8', errors='replace')
    if out_data.strip():
        out(out_data.rstrip())
    if err_data.strip():
        out("[stderr] " + err_data.rstrip())
    return out_data, err_data

out("=" * 60)
out("DEPLOY SCRIPT: QA & Recipe modules")
out("=" * 60)

# Check local files
out("\n[1] Checking local files...")
files_to_upload = []
for f in FILES:
    local_path = os.path.join(LOCAL_BASE, f.replace("/", os.sep))
    if os.path.exists(local_path):
        out(f"  [OK]  {f}")
        files_to_upload.append(f)
    else:
        out(f"  [SKIP] {f} (not found locally)")

out(f"\n  -> {len(files_to_upload)} files will be uploaded.")

# Connect SSH
out("\n[2] Connecting to server...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=30)
out("  Connected!")

# SFTP upload
out("\n[3] Uploading files via SFTP...")
sftp = ssh.open_sftp()

def sftp_makedirs(sftp, remote_dir):
    dirs = []
    path = remote_dir
    while path not in ('/', ''):
        dirs.append(path)
        path = path.rsplit('/', 1)[0]
    dirs.reverse()
    for d in dirs:
        try:
            sftp.stat(d)
        except FileNotFoundError:
            sftp.mkdir(d)

for f in files_to_upload:
    local_path = os.path.join(LOCAL_BASE, f.replace("/", os.sep))
    remote_path = REMOTE_BASE + "/" + f
    remote_dir = remote_path.rsplit("/", 1)[0]
    sftp_makedirs(sftp, remote_dir)
    sftp.put(local_path, remote_path)
    out(f"  Uploaded: {f}")

sftp.close()
out("  All files uploaded.")

# Run artisan migrate
out("\n[4] Running: php artisan migrate --force")
run_cmd(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force")

# Clear caches
out("\n[5] Clearing config/route/cache...")
run_cmd(ssh, f"cd {REMOTE_BASE} && php artisan config:clear && php artisan route:clear && php artisan cache:clear")

# npm build
out("\n[6] Running: npm run build")
run_cmd(ssh, f"cd {REMOTE_BASE} && npm run build 2>&1 | tail -8")

# Health check
out("\n[7] Health check: https://somekorean.com/")
run_cmd(ssh, 'curl -s -o /dev/null -w "%{http_code}" https://somekorean.com/')

ssh.close()
out("\n" + "=" * 60)
out("DEPLOY COMPLETE")
out("=" * 60)
