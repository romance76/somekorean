import paramiko
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

def run_ssh(cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    if out:
        sys.stdout.buffer.write(out.encode('utf-8', errors='replace'))
    if err:
        sys.stderr.buffer.write(err.encode('utf-8', errors='replace'))
    sys.exit(exit_code)

if __name__ == '__main__':
    run_ssh(sys.argv[1])
