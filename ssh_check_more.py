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

# Check the api URL prefix to understand why /api/admin/shorts returns 404
print("=== Check nginx config ===")
out, err = ssh_cmd(client, "cat /etc/nginx/sites-enabled/somekorean 2>/dev/null || cat /etc/nginx/sites-available/default 2>/dev/null | grep -A5 'location' | head -40")
print(out[:500])

# Try with domain name
print("\n=== Check with HTTPS localhost ===")
out, err = ssh_cmd(client, "curl -s -o /dev/null -w '%{http_code}' -k https://localhost/api/admin/shorts 2>&1")
print("HTTPS localhost:", out.strip())

# Check what domain is set
print("\n=== Check .env for APP_URL ===")
out, err = ssh_cmd(client, "grep APP_URL /var/www/somekorean/.env 2>/dev/null | head -3")
print(out.strip())

# Try with 127.0.0.1 and port
print("\n=== Curl via 127.0.0.1 ===")
out, err = ssh_cmd(client, "curl -sv -o /dev/null http://127.0.0.1/api/admin/shorts 2>&1 | grep -E '< HTTP|Location'")
print(out.strip())

# Check php artisan route list for admin/shorts
print("\n=== php artisan route:list (shorts) ===")
out, err = ssh_cmd(client, "cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep 'admin.*shorts' | head -10")
print(out.strip())

# List all admin routes
print("\n=== Admin route list (sample) ===")
out, err = ssh_cmd(client, "cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep '/api/admin/' | head -20")
print(out.strip())

# Check AdminLayout navGroups vs router
# navGroups routes:
nav_routes = [
    '/admin/overview',
    '/admin/members',
    '/admin/content',
    '/admin/matching',
    '/admin/friends',
    '/admin/boards',
    '/admin/clubs',
    '/admin/events-admin',
    '/admin/chats',
    '/admin/news-admin',
    '/admin/qa-admin',
    '/admin/recipes-admin',
    '/admin/shorts-admin',
    '/admin/shopping-admin',
    '/admin/ai-admin',
    '/admin/jobs',
    '/admin/market',
    '/admin/realestate-admin',
    '/admin/business',
    '/admin/rides',
    '/admin/groupbuy',
    '/admin/elder',
    '/admin/mentor-admin',
    '/admin/games-admin',
    '/admin/payments',
    '/admin/banners',
    '/admin/system',
    '/admin/menus',
    '/admin/site',
]

# Router children (path is relative to /admin/)
router_paths = [
    'overview',
    'users',
    'content',
    'elder',
    'business',
    'rides',
    'groupbuy',
    'chats',
    'system',
    'members',
    'payments',
    'banners',
    'menus',
    'boards',
    'site',
    'friends',
    'matching',
    'clubs',
    'events-admin',
    'jobs',
    'market',
    'realestate-admin',
    'mentor-admin',
    'news-admin',
    'shorts-admin',
    'shopping-admin',
    'ai-admin',
    'games-admin',
    'qa-admin',
    'recipes-admin',
    'wallet',
]

router_full = ['/admin/' + p for p in router_paths]

print("\n\n=== ROUTE MISMATCH ANALYSIS ===")
print("\nNavGroups routes NOT in router:")
for r in nav_routes:
    if r not in router_full:
        print(f"  MISSING: {r}")

print("\nRouter routes NOT in navGroups (admin-only, expected):")
for r in router_full:
    if r not in nav_routes:
        print(f"  Extra (no menu): {r}")

client.close()
print("\n=== DONE ===")
