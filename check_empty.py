import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

stdin, stdout, stderr = client.exec_command(f'find {APP}/resources/js -name "*.vue" -exec wc -l {{}} \\;')
out = stdout.read().decode('utf-8', errors='replace')
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.buffer.flush()

client.close()
