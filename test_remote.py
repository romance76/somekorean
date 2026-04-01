import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Write token script
token_php = r"""<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$u = App\Models\User::first();
if (!$u) { echo "NO_USER"; exit; }
echo "USER:" . $u->id . ":" . $u->name . ":" . $u->email . "\n";
$token = auth('api')->login($u);
echo "TOKEN:" . $token;
"""

# Write file via sftp
sftp = client.open_sftp()
with sftp.file('/tmp/get_token.php', 'w') as f:
    f.write(token_php)
sftp.close()

out, err = run('cd /var/www/somekorean && php /tmp/get_token.php 2>&1')
print("TOKEN OUTPUT:", out)
if err:
    print("ERR:", err[:300])

client.close()
