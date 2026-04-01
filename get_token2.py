import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

# PHP 파일을 직접 서버에서 생성
cmd = r"""cat > /tmp/get_token.php << 'HEREDOC'
<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$u = App\Models\User::first();
echo auth('api')->login($u);
HEREDOC"""

stdin, stdout, stderr = ssh.exec_command(cmd)
exit_status = stdout.channel.recv_exit_status()
print('Write status:', exit_status)

# 파일 확인
stdin, stdout, stderr = ssh.exec_command('cat /tmp/get_token.php')
print('File content:')
print(stdout.read().decode())

# 토큰 생성
stdin, stdout, stderr = ssh.exec_command('cd /var/www/somekorean && php /tmp/get_token.php 2>&1')
result = stdout.read().decode().strip()
print('Token result:', result[:200] if len(result) > 200 else result)

ssh.close()
