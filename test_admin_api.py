import paramiko, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=60):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()

# Write PHP test script
php_script = r"""<?php
require "/var/www/somekorean/vendor/autoload.php";
$app = require_once "/var/www/somekorean/bootstrap/app.php";
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$user = \App\Models\User::where("is_admin",1)->first();
echo "Admin user: " . $user->email . "\n";
$token = \Tymon\JWTAuth\Facades\JWTAuth::fromUser($user);
echo "Token: " . $token . "\n";
"""
with open('/tmp/test_sk_api.php', 'w') as f:
    f.write(php_script)

# Upload and run
import base64
enc = base64.b64encode(php_script.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/test_sk_api.php")
result = ssh('cd /var/www/somekorean && php /tmp/test_sk_api.php 2>&1')
print(result)

# Extract token and test API
lines = result.split('\n')
token = ''
for line in lines:
    if 'Token:' in line:
        token = line.replace('Token:', '').strip()
        break

if token:
    print(f"\nToken found: {token[:50]}...")
    # Test admin/games endpoint
    api_result = ssh(f'curl -sk https://somekorean.com/api/admin/games -H "Authorization: Bearer {token}" | head -c 500')
    print("\n=== API Response ===")
    print(api_result)
else:
    print("No token found")

c.close()
