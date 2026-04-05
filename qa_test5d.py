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

# Debug: check if User model has HasApiTokens
print("=== Check User model for token support ===")
out, err = run('cd /var/www/somekorean && grep -n "HasApiTokens\|Sanctum\|createToken" app/Models/User.php | head -10')
print(out)
print()

# Try login to get a token
print("=== Login with real credentials ===")
out, err = run('cd /var/www/somekorean && php artisan tinker --execute="echo App\\\\Models\\\\User::find(1)->email;"')
print(f"User 1 email: {out}")

# Check what auth method is used
out, err = run('cd /var/www/somekorean && grep -rn "createToken\|sanctum\|passport" routes/api.php | head -10')
print(f"Auth in routes: {out}")
print()

# Check AuthController login
out, err = run('cd /var/www/somekorean && cat app/Http/Controllers/API/AuthController.php | head -80')
print("=== AuthController login method ===")
print(out)
print()

# Try to login via API with actual user credentials
out, err = run('cd /var/www/somekorean && php artisan tinker --execute="\\$u = App\\\\Models\\\\User::first(); echo \\$u->email . \\\"\\n\\\" . \\$u->name;"')
print(f"First user: {out}")
print()

# Check if there's a different auth mechanism - maybe JWT
out, err = run('cd /var/www/somekorean && grep -rn "jwt\|JWT\|tymon" composer.json | head -5')
print(f"JWT in composer: {out}")

out, err = run('cd /var/www/somekorean && grep -rn "sanctum\|Sanctum" composer.json | head -5')
print(f"Sanctum in composer: {out}")
print()

# Check auth controller for token generation method
out, err = run('cd /var/www/somekorean && grep -n "token\|Token" app/Http/Controllers/API/AuthController.php | head -20')
print(f"Token references in AuthController: {out}")
print()

ssh.close()
