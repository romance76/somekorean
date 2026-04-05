import paramiko, base64, sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=180):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# Read the CURRENT file (already partially modified from team2_map.py)
print("Reading current BusinessDetail.vue...")
raw_b64 = ssh('base64 -w 0 /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue', timeout=60)
content = base64.b64decode(raw_b64).decode('utf-8')
print(f"File length: {len(content)} chars, lines: {content.count(chr(10))}")

# Print lines 118-130 to see current state
lines = content.split('\n')
print("\nLines 115-135:")
for i in range(114, min(135, len(lines))):
    print(f"{i+1}: {lines[i]}")

print("\nLooking for iframe...")
for i, line in enumerate(lines):
    if 'iframe' in line.lower() or 'maps.google' in line.lower():
        print(f"Found at line {i+1}: {line}")

print("\nLooking for style tag...")
for i, line in enumerate(lines):
    if '<style' in line or '</style>' in line:
        print(f"Line {i+1}: {line}")
