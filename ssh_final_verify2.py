# -*- coding: utf-8 -*-
import paramiko
import sys
import os

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

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

print("=" * 60)
print("FINAL AUDIT VERIFICATION")
print("=" * 60)

# 1. AdminLayout menu groups count
out, _ = ssh_cmd(client, f"grep -c '{{ label:' {APP}/resources/js/pages/admin/AdminLayout.vue")
group_count = out.strip()
print(f"\n[1] AdminLayout navGroups count: {group_count}")

# Check the exact 9 group labels
out, _ = ssh_cmd(client, f"grep \"label:\" {APP}/resources/js/pages/admin/AdminLayout.vue | head -20")
group_lines = [l.strip() for l in out.strip().split('\n') if "label: '" in l or 'label: "' in l]
print(f"    Group labels ({len(group_lines)}):", group_lines)

# 2. AdminShorts API
print("\n[2] AdminShorts.vue API:")
out, _ = ssh_cmd(client, f"grep -E \"axios\\.(get|patch|delete)\" {APP}/resources/js/pages/admin/AdminShorts.vue")
# Parse only function call lines
api_lines = [l.strip() for l in out.strip().split('\n') if 'axios.' in l and '/api/' in l]
for l in api_lines:
    print(f"    {l}")
out2, _ = ssh_cmd(client, f"grep -c 'previewShort' {APP}/resources/js/pages/admin/AdminShorts.vue")
print(f"    Preview modal refs: {out2.strip()} (>0 = PASS)")

# 3. AdminRecipes.vue
print("\n[3] AdminRecipes.vue:")
out, _ = ssh_cmd(client, f"grep -c 'viewModal' {APP}/resources/js/pages/admin/AdminRecipes.vue")
print(f"    viewModal refs: {out.strip()} (>0 = PASS)")
out, _ = ssh_cmd(client, f"grep -c 'editModal' {APP}/resources/js/pages/admin/AdminRecipes.vue")
print(f"    editModal refs: {out.strip()} (>0 = PASS)")
out, _ = ssh_cmd(client, f"grep -c 'recipeStats' {APP}/resources/js/pages/admin/AdminRecipes.vue")
print(f"    recipeStats card: {out.strip()} (>0 = PASS)")
out, _ = ssh_cmd(client, f"grep -c 'ingredients\\|steps' {APP}/resources/js/pages/admin/AdminRecipes.vue")
print(f"    ingredients/steps in detail modal: {out.strip()} (>0 = PASS)")

# 4. Business.vue 4 tabs
print("\n[4] Business.vue tabs:")
out, _ = ssh_cmd(client, f"grep -E \"id:'(list|claims|reviews|crawl)'\" {APP}/resources/js/pages/admin/Business.vue")
tabs = [l.strip() for l in out.strip().split('\n') if l.strip()]
print(f"    Tabs found ({len(tabs)}):")
for t in tabs:
    print(f"      {t}")
api_calls = []
out2, _ = ssh_cmd(client, f"grep \"axios.get\" {APP}/resources/js/pages/admin/Business.vue")
for l in out2.strip().split('\n'):
    if '/api/' in l:
        api_calls.append(l.strip())
print(f"    API calls ({len(api_calls)}):")
for a in api_calls:
    print(f"      {a}")

# 5. AdminController.php shorts
print("\n[5] AdminController shorts methods:")
out, _ = ssh_cmd(client, f"grep 'function.*[Ss]hort' {APP}/app/Http/Controllers/API/AdminController.php")
for l in out.strip().split('\n'):
    print(f"    {l.strip()}")
# Check platform filter added
out2, _ = ssh_cmd(client, f"grep -c 'platform' {APP}/app/Http/Controllers/API/AdminController.php")
print(f"    platform/status filter in getShorts: refs={out2.strip()} (>0 = PASS)")

# 6. api.php shorts routes
print("\n[6] api.php shorts routes:")
out, _ = ssh_cmd(client, f"grep 'shorts' {APP}/routes/api.php")
for l in out.strip().split('\n'):
    if l.strip():
        print(f"    {l.strip()}")

# 7. api.php recipes routes
print("\n[7] api.php recipes routes:")
out, _ = ssh_cmd(client, f"grep \"admin.*recipes\\|AdminRecipeController\" {APP}/routes/api.php | head -12")
for l in out.strip().split('\n'):
    if l.strip():
        print(f"    {l.strip()}")

# 8. API 401 test
print("\n[8] API test GET /api/admin/shorts (no auth):")
out, _ = ssh_cmd(client, 'curl -sk -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid_token" https://somekorean.com/api/admin/shorts')
status = out.strip()
print(f"    HTTP {status} {'PASS (401)' if status == '401' else 'FAIL'}")

# 9. Router duplicate check
print("\n[9] router/index.js duplicate routes:")
out, _ = ssh_cmd(client, f"grep -oP \"path: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
dups = out.strip()
print(f"    Duplicate paths: {dups if dups else 'NONE - PASS'}")

# 10. NavGroups vs Router
print("\n[10] NavGroups routes in router:")
nav_routes = [
    'overview','members','content','matching','friends',
    'boards','clubs','events-admin','chats',
    'news-admin','qa-admin','recipes-admin','shorts-admin','shopping-admin','ai-admin',
    'jobs','market','realestate-admin','business',
    'rides','groupbuy','elder','mentor-admin',
    'games-admin','payments',
    'banners','system',
    'menus','site',
]
out, _ = ssh_cmd(client, f"grep -oP \"path: '([^']+)'\" {APP}/resources/js/router/index.js")
router_paths = [line.split("'")[1] for line in out.strip().split('\n') if line.strip()]

missing = []
for r in nav_routes:
    full = f'/admin/{r}'
    if full not in router_paths:
        missing.append(full)

if missing:
    print(f"    MISSING from router: {missing}")
else:
    print(f"    All {len(nav_routes)} nav menu routes exist in router - PASS")

client.close()

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
