import paramiko, sys
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
stdin, stdout, stderr = client.exec_command('cd /var/www/somekorean && php artisan events:seed --count=1 2>&1', timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.buffer.flush()
client.close()
