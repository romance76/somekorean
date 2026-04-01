import paramiko, sys, base64
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=120):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR:'+e) if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

# Read current file
raw = ssh('base64 /var/www/somekorean/resources/js/pages/admin/Business.vue')
content = base64.b64decode(raw).decode('utf-8')

# Check for backslash-backtick sequences
print("Looking for escaped backticks...")
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if '\\`' in line:
        print(f"  Line {i}: {line[:100]}")

# Fix: replace \` with actual backtick
fixed = content.replace('\\`', '`')

# Also check for the template literal lines
print("\nFixed lines with backticks:")
for i, line in enumerate(fixed.splitlines(), 1):
    if '`/api/' in line:
        print(f"  Line {i}: {line[:100]}")

print("\nWriting fixed file...")
result = write_file('/var/www/somekorean/resources/js/pages/admin/Business.vue', fixed)
print(result)

print("\nRunning npm build...")
r = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=300)
print(r[-1500:])
c.close()
