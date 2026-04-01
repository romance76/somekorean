import paramiko
import json
import requests

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

print("=== CHECKING MISSING/ADDITIONAL FEATURES ===")

# Check if there's a DM/Message model
out, err = run("ls /var/www/somekorean/app/Models/ | grep -iE 'dm|direct|message|pm'")
print(f"\nDM-related models: {out.strip() or 'NONE'}")

out, err = run("ls /var/www/somekorean/app/Models/")
print(f"\nAll models: {out.strip()}")

# Check MessageController
out, err = run("cat /var/www/somekorean/app/Http/Controllers/API/MessageController.php 2>/dev/null | head -80")
print(f"\nMessageController: {out[:1000] or 'NOT FOUND'}")

# Check Message model
out, err = run("cat /var/www/somekorean/app/Models/Message.php 2>/dev/null | head -50")
print(f"\nMessage model: {out[:500] or 'NOT FOUND'}")

# Check routes for messages
out, err = run("grep -n 'message\|dm\|direct' /var/www/somekorean/routes/api.php | head -30")
print(f"\nMessage routes: {out}")

# Check match block feature
out, err = run("grep -n 'block\|ban' /var/www/somekorean/app/Http/Controllers/API/MatchController.php")
print(f"\nMatch block in MatchController: {out.strip() or 'NOT FOUND'}")

# Check user_blocks table
out, err = run("cd /var/www/somekorean && php artisan tinker --execute=\"DB::statement('SHOW CREATE TABLE user_blocks')\" 2>&1 | tail -5")
print(f"\nuser_blocks table: {out}")

# Check match_profile table structure
out, err = run("cd /var/www/somekorean && php artisan tinker --execute=\"DB::select('DESCRIBE match_profiles')\" 2>&1")
print(f"\nmatch_profiles structure: {out[:500]}")

# Check ChatRoom model for DM support
out, err = run("cat /var/www/somekorean/app/Models/ChatRoom.php 2>/dev/null")
print(f"\nChatRoom model: {out[:1000] or 'NOT FOUND'}")

client.close()
