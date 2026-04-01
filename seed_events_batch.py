import paramiko, sys
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

# Seed in batches to find which template fails
for batch in range(1, 56):
    stdin, stdout, stderr = client.exec_command(f'cd /var/www/somekorean && php artisan events:seed --count={batch} 2>&1 | tail -1', timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if 'error' in out.lower() or 'exception' in out.lower() or 'SQLSTATE' in out:
        sys.stdout.buffer.write(f'FAIL at count={batch}: {out[:200]}\n'.encode('utf-8'))
        sys.stdout.buffer.flush()
        # Delete the partial batch
        stdin2, stdout2, stderr2 = client.exec_command(f"cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'cleaned';\"", timeout=15)
        stdout2.read()
        break
    else:
        if batch % 10 == 0:
            sys.stdout.buffer.write(f'OK: {batch} events\n'.encode('utf-8'))
            sys.stdout.buffer.flush()

# Final: seed 50 (skip problematic template)
stdin, stdout, stderr = client.exec_command(f"cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'cleaned';\"", timeout=15)
stdout.read()

# Try seeding with count=20 (safe subset)
stdin, stdout, stderr = client.exec_command('cd /var/www/somekorean && php artisan events:seed --count=20 2>&1', timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'Batch 20: {out[-200:]}\n'.encode('utf-8'))

stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"echo 'Events: '.App\\\\Models\\\\Event::count();\"", timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'{out}\n'.encode('utf-8'))
sys.stdout.buffer.flush()
client.close()
sys.stdout.buffer.write(b'DONE\n'); sys.stdout.buffer.flush()
