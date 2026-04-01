import paramiko
import sys
import os

def log(msg):
    sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
    sys.stdout.buffer.flush()

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP_PATH = "/var/www/somekorean"
LOCAL_BASE = r"C:\Users\Admin\Desktop\somekorean\server_files"

files_to_upload = [
    "resources/js/pages/admin/Chats.vue",
]

log("=== Deploy Chat Fix ===")
log(f"Host: {HOST}")
log(f"App Path: {APP_PATH}")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

log("\n[1] Connecting to server...")
ssh.connect(HOST, username=USER, password=PASS, timeout=30)
log("Connected.")

sftp = ssh.open_sftp()

log("\n[2] Uploading files...")
for rel_path in files_to_upload:
    local_path = os.path.join(LOCAL_BASE, rel_path.replace("/", os.sep))
    remote_path = APP_PATH + "/" + rel_path
    remote_dir = remote_path.rsplit("/", 1)[0]

    # Ensure remote directory exists
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_dir}")
    stdout.channel.recv_exit_status()

    log(f"  Uploading: {rel_path}")
    log(f"    Local:  {local_path}")
    log(f"    Remote: {remote_path}")

    if not os.path.exists(local_path):
        log(f"    ERROR: Local file not found: {local_path}")
        sftp.close()
        ssh.close()
        sys.exit(1)

    sftp.put(local_path, remote_path)
    log(f"    Upload complete.")

sftp.close()
log("\n[3] Running npm build...")
stdin, stdout, stderr = ssh.exec_command(
    f"cd {APP_PATH} && npm run build 2>&1 | tail -5",
    timeout=300
)
exit_status = stdout.channel.recv_exit_status()
build_output = stdout.read().decode('utf-8', errors='replace')
log(f"Build output (last 5 lines):\n{build_output}")
log(f"Build exit status: {exit_status}")

log("\n[4] Checking site HTTP status...")
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://somekorean.com/',
    timeout=30
)
stdout2.channel.recv_exit_status()
http_code = stdout2.read().decode('utf-8', errors='replace').strip()
log(f"HTTP Status Code: {http_code}")

ssh.close()
log("\n=== Deployment Complete ===")
