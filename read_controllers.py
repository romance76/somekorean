import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Read controllers
for ctrl in ['ChatController', 'MatchController', 'FriendController']:
    out, err = run(f'cat /var/www/somekorean/app/Http/Controllers/API/{ctrl}.php')
    print(f"\n{'='*60}")
    print(f"=== {ctrl} ===")
    print('='*60)
    print(out[:8000])

# Read routes
out, err = run('cat /var/www/somekorean/routes/api.php')
print("\n" + "="*60)
print("=== API ROUTES ===")
print("="*60)
print(out[:5000])

client.close()
