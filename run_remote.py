import paramiko
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def run(cmd, timeout=120):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=10)
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    code = stdout.channel.recv_exit_status()
    ssh.close()
    if out:
        print(out, end='')
    if err:
        print(err, end='', file=sys.stderr)
    return code

def upload(local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=10)
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"Uploaded {local_path} -> {remote_path}")

if __name__ == '__main__':
    if sys.argv[1] == '--upload':
        upload(sys.argv[2], sys.argv[3])
    else:
        code = run(sys.argv[1])
        sys.exit(code)
