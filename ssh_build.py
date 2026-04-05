import paramiko

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

print("=== npm run build ===")
out, err = ssh_cmd(client, f"cd {APP} && npm run build 2>&1 | tail -20", timeout=300)
print(out[-1000:])
if err.strip():
    print("STDERR:", err[:500])

client.close()
print("=== DONE ===")
