import paramiko, sys
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    sys.stdout.buffer.write(f'{out[-300:]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

# Clean old seeded events, keep original 20
run("cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'Cleaned old events';\"")

# Seed 50 fresh
run('cd /var/www/somekorean && php artisan events:seed --count=50 2>&1')

# Count
run("cd /var/www/somekorean && php artisan tinker --execute=\"echo 'Total events: '.App\\\\Models\\\\Event::count();\"")
client.close()
sys.stdout.buffer.write(b'DONE\n'); sys.stdout.buffer.flush()
