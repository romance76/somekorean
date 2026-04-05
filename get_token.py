import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

# PHP 스크립트 내용을 echo 명령어로 작성
lines = [
    "<?php",
    "require '/var/www/somekorean/vendor/autoload.php';",
    "$app = require_once '/var/www/somekorean/bootstrap/app.php';",
    "$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);",
    "$kernel->bootstrap();",
    "$u = App\\Models\\User::first();",
    "echo auth('api')->login($u);"
]

# printf로 파일 작성
php_content = "\n".join(lines)
stdin, stdout, stderr = ssh.exec_command("printf '%s' " + repr(php_content) + " > /tmp/get_token.php")
stdout.channel.recv_exit_status()

# 파일 확인
stdin, stdout, stderr = ssh.exec_command('cat /tmp/get_token.php')
print('PHP FILE:', stdout.read().decode())

# 토큰 생성
stdin, stdout, stderr = ssh.exec_command('cd /var/www/somekorean && php /tmp/get_token.php 2>&1')
result = stdout.read().decode().strip()
print('TOKEN RESULT:', result)

ssh.close()
