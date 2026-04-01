import paramiko
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# Check tinker error
print("=== Debugging tinker ===")
out, err = run('cd /var/www/somekorean && php artisan tinker --execute="echo App\\\\Models\\\\User::find(1)->name;"')
print(f"OUT: {out}")
print(f"ERR: {err}")
print()

# Try alternative token creation
print("=== Token via raw PHP ===")
out, err = run("""cd /var/www/somekorean && php -r '
require "vendor/autoload.php";
\$app = require_once "bootstrap/app.php";
\$app->make("Illuminate\\Contracts\\Console\\Kernel")->bootstrap();
\$user = App\\Models\\User::find(1);
echo \$user->createToken("test5")->plainTextToken;
'""")
print(f"User1 Token OUT: {out[-80:]}")
print(f"ERR: {err[:200]}")
print()

out2, err2 = run("""cd /var/www/somekorean && php -r '
require "vendor/autoload.php";
\$app = require_once "bootstrap/app.php";
\$app->make("Illuminate\\Contracts\\Console\\Kernel")->bootstrap();
\$user = App\\Models\\User::find(272);
echo \$user->createToken("admin-test5")->plainTextToken;
'""")
print(f"Admin Token OUT: {out2[-80:]}")
print(f"ERR: {err2[:200]}")
print()

# Check routes
print("=== Checking API routes ===")
out, err = run('cd /var/www/somekorean && php artisan route:list --path=api/login 2>/dev/null | head -20')
print(out)
print()

out, err = run('cd /var/www/somekorean && php artisan route:list --path=api/register 2>/dev/null | head -20')
print(out)
print()

out, err = run('cd /var/www/somekorean && php artisan route:list --path=api/user 2>/dev/null | head -30')
print(out)
print()

out, err = run('cd /var/www/somekorean && php artisan route:list --path=api/admin 2>/dev/null | head -30')
print(out)
print()

ssh.close()
