import paramiko, base64, sys, os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=180):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    result = out.read().decode('utf-8', errors='replace').strip()
    error = err.read().decode('utf-8', errors='replace').strip()
    if error and 'warning' not in error.lower():
        return result + "\nSTDERR: " + error
    return result

def write_file_from_local(remote_path, local_path):
    with open(local_path, 'rb') as f:
        content = f.read()
    enc = base64.b64encode(content).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for chunk in chunks:
        ssh(f"printf '%s' '{chunk}' >> /tmp/wf_chunk")
    ssh(f"cat /tmp/wf_chunk | base64 -d > {remote_path} && rm -f /tmp/wf_chunk")
    size = ssh(f'wc -c < {remote_path}')
    print(f"Written {remote_path}: {size} bytes")

def write_file(remote_path, content_str):
    enc = base64.b64encode(content_str.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for chunk in chunks:
        ssh(f"printf '%s' '{chunk}' >> /tmp/wf_chunk")
    ssh(f"cat /tmp/wf_chunk | base64 -d > {remote_path} && rm -f /tmp/wf_chunk")
    size = ssh(f'wc -c < {remote_path}')
    print(f"Written {remote_path}: {size} bytes")

# Step 1: Upload GameColors.vue from local file
local_vue = os.path.join(os.path.dirname(__file__), 'GameColors.vue')
write_file_from_local('/var/www/somekorean/resources/js/pages/games/GameColors.vue', local_vue)

# Step 2: Read router and add route after game-counting line
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
print("=== Router game lines ===")
lines = router_content.split('\n')
for i, line in enumerate(lines):
    if 'game' in line.lower() or 'counting' in line.lower() or 'color' in line.lower():
        print(f"  {i+1}: {line}")

# Find game-counting line and insert after it
new_route = "  { path: '/games/colors', component: () => import('../pages/games/GameColors.vue'), name: 'game-colors' },"
new_lines = []
inserted = False
for line in lines:
    new_lines.append(line)
    if not inserted and ('game-counting' in line or 'GameCounting' in line or 'counting' in line.lower()):
        new_lines.append(new_route)
        inserted = True
        print(f"Inserted route after: {line.strip()}")

if not inserted:
    print("WARNING: Could not find game-counting line. Looking for games section...")
    # Try to insert before the closing of routes array
    new_lines = []
    for line in lines:
        if not inserted and ('},' in line and 'game' in line.lower()):
            new_lines.append(line)
            new_lines.append(new_route)
            inserted = True
            print(f"Inserted route after: {line.strip()}")
        else:
            new_lines.append(line)

if inserted:
    new_router = '\n'.join(new_lines)
    write_file('/var/www/somekorean/resources/js/router/index.js', new_router)
    print("Router updated!")
else:
    print("ERROR: Could not insert route - please check router manually")

c.close()
print("=== Files deployed ===")
