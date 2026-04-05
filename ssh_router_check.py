# -*- coding: utf-8 -*-
import paramiko
import sys
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

# Admin routes are defined as children with relative paths like 'overview', 'members', etc.
# The navGroups use full paths like '/admin/overview'
# We need to check the admin children in router

# Extract children of /admin route
out, _ = ssh_cmd(client, f"cat {APP}/resources/js/router/index.js")
lines = out.split('\n')

# Find the admin children section
in_admin = False
admin_children = []
for line in lines:
    if "path: '/admin'" in line:
        in_admin = True
    if in_admin and "{ path: '" in line:
        import re
        m = re.search(r"path: '([^']+)'", line)
        if m:
            p = m.group(1)
            if p.startswith('/'):
                # This is the /admin route itself, skip
                continue
            admin_children.append(p)
    if in_admin and "],\n" in line and "children" not in line:
        if len(admin_children) > 5:  # we've collected children
            in_admin = False

print("Admin router children paths:")
for c in sorted(admin_children):
    print(f"  {c}")

# NavGroups paths (without /admin/ prefix)
nav_paths = [
    'overview','members','content','matching','friends',
    'boards','clubs','events-admin','chats',
    'news-admin','qa-admin','recipes-admin','shorts-admin','shopping-admin','ai-admin',
    'jobs','market','realestate-admin','business',
    'rides','groupbuy','elder','mentor-admin',
    'games-admin','payments',
    'banners','system',
    'menus','site',
]

print(f"\nNavGroups has {len(nav_paths)} menu items")
print("\nNavGroup items NOT in router children:")
missing = [p for p in nav_paths if p not in admin_children]
if missing:
    for m in missing:
        print(f"  MISSING: {m}")
else:
    print("  NONE - all nav routes covered")

print("\nRouter admin children NOT in navGroups (hidden routes, OK):")
extra = [c for c in admin_children if c not in nav_paths and c not in ('', 'redirect')]
for e in extra:
    print(f"  Extra: {e}")

client.close()
