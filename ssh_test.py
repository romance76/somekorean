import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
    print("SSH connected!")

    tok_php = (
        "<?php\n"
        "require '/var/www/somekorean/vendor/autoload.php';\n"
        "$app = require_once '/var/www/somekorean/bootstrap/app.php';\n"
        "$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);\n"
        "$kernel->bootstrap();\n"
        "$u1 = \\App\\Models\\User::first();\n"
        "$u2 = \\App\\Models\\User::skip(1)->first();\n"
        "$t1 = auth('api')->login($u1);\n"
        "$t2 = auth('api')->login($u2);\n"
        "echo $u1->id.'|'.$u2->id.'|'.$t1.'|'.$t2;\n"
    )

    sftp = client.open_sftp()
    with sftp.open('/tmp/tok.php', 'w') as f:
        f.write(tok_php)
    sftp.close()
    print("tok.php written")

    stdin, stdout, stderr = client.exec_command("php /tmp/tok.php 2>/dev/null")
    result = stdout.read().decode().strip()
    err = stderr.read().decode()
    print(f"TOKENS: {result}")
    if err:
        print(f"STDERR: {err[:300]}")
    client.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
