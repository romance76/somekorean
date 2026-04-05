import paramiko
import time

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd_stream(client, cmd, timeout=300):
    """Stream output line by line with timeout."""
    transport = client.get_transport()
    channel = transport.open_session()
    channel.settimeout(timeout)
    channel.exec_command(cmd)

    output = []
    start = time.time()
    while True:
        if channel.recv_ready():
            data = channel.recv(4096).decode('utf-8', errors='replace')
            output.append(data)
        if channel.exit_status_ready():
            break
        if time.time() - start > timeout:
            output.append("\n[TIMEOUT]")
            break
        time.sleep(0.5)

    # Drain any remaining
    while channel.recv_ready():
        data = channel.recv(4096).decode('utf-8', errors='replace')
        output.append(data)

    return ''.join(output), channel.recv_exit_status()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

print("=== Running npm run build (may take 2-3 minutes) ===")
out, code = ssh_cmd_stream(client, f"cd {APP} && npm run build 2>&1", timeout=300)
lines = out.split('\n')
# Print last 30 lines
print('\n'.join(lines[-30:]))
print(f"\nExit code: {code}")

client.close()
print("=== DONE ===")
