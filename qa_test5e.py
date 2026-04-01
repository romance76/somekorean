import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

# Find actual routes for dashboard, profile, bookmarks, points
print("=== All api/user routes ===")
out, _ = run(r'cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep "api/" | grep -i "dashboard\|profile\|bookmark\|point\|user/" | head -30')
print(out)
print()

# Check if there's a /api/me/dashboard or similar
print("=== Routes with dashboard/profile/bookmark/point ===")
out, _ = run(r'cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep -i "dashboard\|profile\|bookmark\|point" | head -30')
print(out)
print()

# Also check /api/admin/dashboard specifically
print("=== Admin dashboard route ===")
out, _ = run(r'cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep -i "admin.*dash" | head -10')
print(out)
print()

# Check the actual user-related routes
print("=== All user-related API routes ===")
out, _ = run(r'cd /var/www/somekorean && php artisan route:list 2>/dev/null | grep "api/" | grep -v "sanctum" | head -80')
print(out)
print()

ssh.close()
