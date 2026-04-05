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

print("=" * 60)
print("FINAL AUDIT VERIFICATION")
print("=" * 60)

# 1. AdminLayout menu groups
out, _ = ssh_cmd(client, f"grep -c \"label:\" {APP}/resources/js/pages/admin/AdminLayout.vue")
print(f"\n1. AdminLayout menu groups: {out.strip()} (expected 9)")

# 2. AdminShorts API endpoints
print("\n2. AdminShorts.vue API calls:")
out, _ = ssh_cmd(client, f"grep \"axios\\.(get\\|post\\|patch\\|delete\\|put)\" {APP}/resources/js/pages/admin/AdminShorts.vue")
print(out.strip())

# 3. AdminRecipes.vue modals + stats
print("\n3. AdminRecipes.vue features:")
out, _ = ssh_cmd(client, f"grep -c 'viewModal\\|editModal\\|recipeStats' {APP}/resources/js/pages/admin/AdminRecipes.vue")
print(f"  refs found: {out.strip()} (viewModal, editModal, recipeStats)")

# 4. Business.vue 4 tabs
print("\n4. Business.vue tabs:")
out, _ = ssh_cmd(client, f"grep \"id:'\" {APP}/resources/js/pages/admin/Business.vue")
print(out.strip())

# 5. AdminController shorts methods
print("\n5. AdminController shorts methods:")
out, _ = ssh_cmd(client, f"grep 'function.*Short\\|function getShorts' {APP}/app/Http/Controllers/API/AdminController.php")
print(out.strip())

# 6. api.php shorts + recipes routes
print("\n6. api.php admin shorts routes:")
out, _ = ssh_cmd(client, f"grep \"admin.*shorts\\|shorts.*admin\" {APP}/routes/api.php")
print(out.strip())

print("\n7. api.php admin recipes routes:")
out, _ = ssh_cmd(client, f"grep \"recipes\" {APP}/routes/api.php | grep -v '#'")
print(out.strip()[:600])

# 7. API test
print("\n8. API test: GET /api/admin/shorts")
out, _ = ssh_cmd(client, 'curl -sk -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid" https://somekorean.com/api/admin/shorts')
print(f"  Response: {out.strip()} (expected 401)")

# 8. Router duplicate check
print("\n9. Router duplicate routes check:")
out, _ = ssh_cmd(client, f"grep -oP \"path: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
print(f"  Duplicate paths: {out.strip() if out.strip() else 'NONE'}")

out, _ = ssh_cmd(client, f"grep -c 'path:' {APP}/resources/js/router/index.js")
print(f"  Total route definitions: {out.strip()}")

# 9. AdminLayout nav groups vs router
print("\n10. NavGroups → Router coverage:")
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
    print(f"  MISSING from router: {missing}")
else:
    print("  All 29 nav menu routes exist in router/index.js - PASS")

client.close()
print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
