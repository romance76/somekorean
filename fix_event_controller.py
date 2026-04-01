import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# Read full EventController.php
print("Reading EventController.php...")
sftp = client.open_sftp()
with sftp.open('/var/www/somekorean/app/Http/Controllers/API/EventController.php', 'r') as f:
    content = f.read().decode('utf-8', errors='replace')

print(f"File size: {len(content)} chars")
print(f"Lines: {content.count(chr(10))}")

# Find the problematic lines
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if '\\$event' in line or '\\$' in line:
        print(f"Line {i}: {repr(line)}")

# Fix the backslash escapes in EventController
# The issue is \$event should be $event (the backslash is a PHP heredoc/shell artifact)
fixed_content = content.replace('\\$event', '$event').replace('\\$', '$')

# Check if fix was needed
changes = content.count('\\$')
print(f"\nFound {changes} \\$ occurrences to fix")

if changes > 0:
    # Write fixed content
    with sftp.open('/var/www/somekorean/app/Http/Controllers/API/EventController.php', 'w') as f:
        f.write(fixed_content)
    print("Fixed EventController.php written")

    # Verify syntax
    out, err = run("php -l /var/www/somekorean/app/Http/Controllers/API/EventController.php 2>&1")
    print(f"PHP syntax check: {out.strip()}")
else:
    print("No \\$ found - checking differently")
    # Print lines around 94
    for i, line in enumerate(lines[89:100], 90):
        print(f"Line {i}: {repr(line)}")

sftp.close()
client.close()
