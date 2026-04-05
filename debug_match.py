import paramiko
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f'>>> {cmd[:90]}')
    if out: print(out[:800])
    if err and 'Warning' not in err: print(f'ERR: {err[:300]}')
    print()

APP = '/var/www/somekorean'

run(f"cd {APP} && php artisan tinker --execute=\"echo 'MP count: '.App\\\\Models\\\\MatchProfile::count();\"")
run(f"cd {APP} && php artisan tinker --execute=\"echo 'Public: '.App\\\\Models\\\\MatchProfile::where('visibility','public')->count();\"")
run(f"cd {APP} && php artisan tinker --execute=\"echo 'Users: '.App\\\\Models\\\\User::count();\"")
run(f"cd {APP} && php artisan tinker --execute=\"\\$p=App\\\\Models\\\\MatchProfile::where('visibility','public')->with('user:id,name,username,avatar')->first(); echo json_encode(\\$p);\"")
run(f"cd {APP} && cat app/Http/Controllers/API/MatchController.php | head -65")
run(f"cd {APP} && tail -20 storage/logs/laravel.log 2>/dev/null")

# Try to simulate browse API call
run(f"cd {APP} && php artisan tinker --execute=\"\\$u = App\\\\Models\\\\User::first(); \\$token = auth('api')->login(\\$u); echo \\$token;\"")

client.close()
