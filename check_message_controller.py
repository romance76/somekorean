import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Read full MessageController
out, err = run("cat /var/www/somekorean/app/Http/Controllers/API/MessageController.php")
print("=== MessageController.php ===")
print(out)

# Check the messages table
out, err = run("cd /var/www/somekorean && php artisan tinker --execute=\"\\$m = new App\\\\Models\\\\Message; echo implode(',', \\$m->getFillable());\" 2>&1")
print(f"\nMessage fillable: {out}")

client.close()
