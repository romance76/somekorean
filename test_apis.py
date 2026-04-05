import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Get token first
token_php = r"""<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$users = App\Models\User::limit(3)->get();
foreach($users as $u) {
    echo "USER:" . $u->id . ":" . $u->name . ":" . $u->email . "\n";
}
$u = App\Models\User::first();
$token = auth('api')->login($u);
echo "TOKEN:" . $token;
"""
sftp = client.open_sftp()
with sftp.file('/tmp/get_token.php', 'w') as f:
    f.write(token_php)

# Get second user token too
token_php2 = r"""<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$u = App\Models\User::skip(1)->first();
if (!$u) { $u = App\Models\User::create(['name'=>'Test User2','email'=>'test2@test.com','password'=>bcrypt('password'),'username'=>'testuser2']); }
$token = auth('api')->login($u);
echo "TOKEN2:" . $token . "\nUSER2:" . $u->id . ":" . $u->email;
"""
with sftp.file('/tmp/get_token2.php', 'w') as f:
    f.write(token_php2)
sftp.close()

out, err = run('cd /var/www/somekorean && php /tmp/get_token.php 2>&1')
print("=== USERS & TOKEN ===")
print(out)

token = None
for line in out.strip().split('\n'):
    if line.startswith('TOKEN:'):
        token = line.replace('TOKEN:', '').strip()

out2, err2 = run('cd /var/www/somekorean && php /tmp/get_token2.php 2>&1')
print("=== USER2 TOKEN ===")
print(out2)
token2 = None
user2_id = None
for line in out2.strip().split('\n'):
    if line.startswith('TOKEN2:'):
        token2 = line.replace('TOKEN2:', '').strip()
    if line.startswith('USER2:'):
        user2_id = line.split(':')[1]

print(f"\nToken1: {token[:50] if token else 'NONE'}...")
print(f"Token2: {token2[:50] if token2 else 'NONE'}...")
print(f"User2 ID: {user2_id}")

client.close()

# Save tokens to file for next script
with open('/tmp/tokens.json', 'w') as f:
    json.dump({'token': token, 'token2': token2, 'user2_id': user2_id}, f)
print("\nTokens saved.")
