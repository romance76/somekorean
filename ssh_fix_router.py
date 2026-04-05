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

out, _ = ssh_cmd(client, f"cat {APP}/resources/js/router/index.js")

# The duplicates are lines 132-151 area and 143-151 area.
# The first set (lines 127-141) is the original block.
# Lines 143-151 appear to be a second accidental paste of the same block.
# We need to remove the duplicate lines (second copy).

# The duplicate block that needs to be removed is:
# (Appears after '/games/car-jump' line, duplicating lines 132-150)
# We'll remove the second occurrence of each duplicate path.

lines = out.split('\n')
seen_paths = set()
seen_names = set()
new_lines = []
removed = []

for line in lines:
    # Extract path and name from route lines
    import re
    path_match = re.search(r"path: '([^']+)'", line)
    name_match = re.search(r"name: '([^']+)'", line)

    if path_match and name_match:
        path = path_match.group(1)
        name = name_match.group(1)
        key = (path, name)
        if key in seen_paths:
            removed.append(line.strip())
            continue
        seen_paths.add(key)
    elif path_match:
        path = path_match.group(1)
        if path in {p for p, _ in seen_paths}:
            # Check if this is a duplicate path with different name
            existing_names = {n for p, n in seen_paths if p == path}
            if name_match is None:
                removed.append(line.strip())
                continue
        if path_match:
            if path in {p for p, _ in seen_paths}:
                removed.append(line.strip())
                continue
            seen_paths.add((path, ''))

    new_lines.append(line)

print(f"Lines removed ({len(removed)}):")
for r in removed:
    print(f"  {r}")

new_content = '\n'.join(new_lines)

sftp = client.open_sftp()
with sftp.open(f"{APP}/resources/js/router/index.js", 'w') as f:
    f.write(new_content)

print("\nrouter/index.js - duplicate routes REMOVED")

# Verify
out2, _ = ssh_cmd(client, f"grep -oP \"path: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
print("Remaining duplicate paths:", out2.strip() if out2.strip() else "NONE")

out3, _ = ssh_cmd(client, f"grep -oP \"name: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
print("Remaining duplicate names:", out3.strip() if out3.strip() else "NONE")

client.close()
print("=== DONE ===")
