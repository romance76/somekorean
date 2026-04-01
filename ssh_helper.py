import paramiko
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
    return ssh

def write_file(remote_path, local_path):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"Written: {remote_path}")

def run_cmd(cmd):
    ssh = get_ssh()
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    ssh.close()
    if out: print(out)
    if err: print("STDERR:", err)
    return out

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'write':
        write_file(sys.argv[2], sys.argv[3])
    elif action == 'cmd':
        run_cmd(' '.join(sys.argv[2:]))
