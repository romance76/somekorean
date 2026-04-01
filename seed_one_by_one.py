import paramiko, sys
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

# Clean first
stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'cleaned';\"", timeout=15)
stdout.read()

# Seed one at a time to find the bad template
for i in range(1, 56):
    stdin, stdout, stderr = client.exec_command(f'cd /var/www/somekorean && php artisan events:seed --count={i} 2>&1 | grep -i "error\\|SQLSTATE\\|created\\|생성" | head -1', timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if 'error' in out.lower() or 'SQLSTATE' in out or not out:
        sys.stdout.buffer.write(f'FAIL at template #{i}\n'.encode('utf-8')); sys.stdout.buffer.flush()
        # Clean and continue from next
        stdin2, stdout2, stderr2 = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'c';\"", timeout=15)
        stdout2.read()
    else:
        if i <= 5 or i % 10 == 0:
            sys.stdout.buffer.write(f'OK #{i}: {out}\n'.encode('utf-8')); sys.stdout.buffer.flush()
        # Clean for next iteration
        stdin2, stdout2, stderr2 = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"App\\\\Models\\\\Event::where('id','>',20)->delete(); echo 'c';\"", timeout=15)
        stdout2.read()

# Now seed with safe count (e.g., 40)
stdin, stdout, stderr = client.exec_command('cd /var/www/somekorean && php artisan events:seed --count=40 2>&1 | tail -1', timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'Final seed 40: {out}\n'.encode('utf-8'))

stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"echo 'Total: '.App\\\\Models\\\\Event::count();\"", timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'{out}\n'.encode('utf-8'))
sys.stdout.buffer.flush()
client.close()
