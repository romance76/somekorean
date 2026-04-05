import paramiko, os, sys
HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()
def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'{out.strip()[:300]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

sftp.put(os.path.join(LOCAL, 'app', 'Models', 'Event.php'), f'{APP}/app/Models/Event.php')
sys.stdout.buffer.write(b'UP: Event.php\n'); sys.stdout.buffer.flush()

# Test events API
run('curl -s https://somekorean.com/api/events | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\'Events: {len(d) if isinstance(d,list) else len(d.get(chr(100)+chr(97)+chr(116)+chr(97),[]))}\')"')
sftp.close(); client.close()
sys.stdout.buffer.write(b'DONE\n'); sys.stdout.buffer.flush()
