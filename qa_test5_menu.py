import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=20):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

out, _ = run(r'cd /var/www/somekorean && php artisan tinker --execute="echo \Tymon\JWTAuth\Facades\JWTAuth::fromUser(\App\Models\User::find(272));"')
admin_token = out.strip().split('\n')[-1].strip()

out, _ = run(f'curl -sk "https://somekorean.com/api/admin/settings/menus" -H "Accept: application/json" -H "Authorization: Bearer {admin_token}" 2>/dev/null')
print("Full menu response:")
print(out[:2000])

ssh.close()
