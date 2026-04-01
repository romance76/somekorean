import paramiko
import json
import subprocess

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

sftp = client.open_sftp()

# Create new tok.php that gets non-admin users
tok_php2 = (
    "<?php\n"
    "require '/var/www/somekorean/vendor/autoload.php';\n"
    "$app = require_once '/var/www/somekorean/bootstrap/app.php';\n"
    "$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);\n"
    "$kernel->bootstrap();\n"
    "$u1 = \\App\\Models\\User::where('is_admin', 0)->first();\n"
    "$u2 = \\App\\Models\\User::where('is_admin', 0)->where('id', '!=', $u1->id)->first();\n"
    "$t1 = auth('api')->login($u1);\n"
    "$t2 = auth('api')->login($u2);\n"
    "echo $u1->id.'|'.$u2->id.'|'.$t1.'|'.$t2.'|'.$u1->name.'|'.$u2->name;\n"
)
with sftp.open('/tmp/tok2.php', 'w') as f:
    f.write(tok_php2)

out, err = run("php /tmp/tok2.php 2>/dev/null")
print(f"Non-admin tokens: {out}")

parts = out.strip().split('|')
if len(parts) >= 4:
    u1_id, u2_id, t1, t2 = parts[0], parts[1], parts[2], parts[3]
    u1_name = parts[4] if len(parts) > 4 else 'user1'
    u2_name = parts[5] if len(parts) > 5 else 'user2'
    print(f"User1 (id={u1_id}, name={u1_name}): token OK")
    print(f"User2 (id={u2_id}, name={u2_name}): token OK")
else:
    print(f"ERROR: {out}")
    print(f"STDERR: {err[:200]}")

sftp.close()
client.close()

# Now save these tokens for use in the final test
print("\n=== TOKENS ===")
print(f"U1_ID={u1_id}")
print(f"U2_ID={u2_id}")
print(f"T1={t1[:50]}...")
print(f"T2={t2[:50]}...")
