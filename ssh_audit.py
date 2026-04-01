import paramiko
import sys

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    return client

if __name__ == "__main__":
    client = connect()
    print("=== CONNECTED ===")

    # List key files
    out, err = ssh_cmd(client, f"find {APP}/resources/js -name 'Admin*.vue' -o -name 'Business.vue' | sort")
    print("=== VUE FILES ===")
    print(out)

    out, err = ssh_cmd(client, f"find {APP}/app/Http/Controllers -name 'AdminController.php' | head -5")
    print("=== CONTROLLERS ===")
    print(out)

    out, err = ssh_cmd(client, f"find {APP}/routes -name 'api.php' | head -5")
    print("=== ROUTES ===")
    print(out)

    client.close()
    print("=== DONE ===")
