#!/usr/bin/env python3
import paramiko, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=30):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip(), stderr.read().decode('utf-8', errors='replace').strip()

# Enable debug mode temporarily
out, _ = ssh("grep APP_DEBUG /var/www/somekorean/.env")
log("Current debug setting: " + out)

# Try with debug enabled
out, _ = ssh("APP_DEBUG=true php -r \"$_SERVER['SERVER_NAME']='somekorean.com'; require '/var/www/somekorean/public/index.php';\" 2>&1 | head -5")

# Check laravel log after request
ssh("curl -sk https://somekorean.com/api/recipes/1 -o /dev/null 2>&1")
out, _ = ssh("tail -30 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null")
log("Laravel log after request:\n" + out)

# Read RecipeController to check show() method
out, _ = ssh("cat /var/www/somekorean/app/Http/Controllers/API/RecipeController.php | grep -A50 'function show'")
log("\nRecipeController show():\n" + out[:2000])

c.close()
