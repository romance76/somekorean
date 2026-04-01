import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

print("=" * 60)
print("서버 진단")
print("=" * 60)

# Check routes
print("\n[1] jobs 라우트 확인")
out, _ = run("cd /var/www/somekorean && php artisan route:list --path=api/jobs 2>/dev/null | head -30")
print(out)

print("\n[2] market 라우트 확인")
out, _ = run("cd /var/www/somekorean && php artisan route:list --path=api/market 2>/dev/null | head -30")
print(out)

print("\n[3] events 라우트 확인")
out, _ = run("cd /var/www/somekorean && php artisan route:list --path=api/events 2>/dev/null | head -30")
print(out)

print("\n[4] realestate 라우트 확인")
out, _ = run("cd /var/www/somekorean && php artisan route:list --path=api/realestate 2>/dev/null | head -30")
print(out)

# Check laravel log
print("\n[5] Laravel 최근 에러 로그 (events/market)")
out, _ = run("tail -80 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -A5 'Error\\|Exception' | head -60")
print(out[:2000])

# Check jobs POST fields
print("\n[6] JobPost model fillable")
out, _ = run("grep -n 'fillable\\|content\\|title\\|type' /var/www/somekorean/app/Models/JobPost.php 2>/dev/null | head -20")
print(out)

# Check jobs controller store method
print("\n[7] Jobs controller store method")
out, _ = run("grep -n 'store\\|validate\\|request' /var/www/somekorean/app/Http/Controllers/Api/JobController.php 2>/dev/null | head -30")
print(out)

# Check market controller
print("\n[8] Market controller store method")
out, _ = run("ls /var/www/somekorean/app/Http/Controllers/Api/ 2>/dev/null")
print(out)

# Check events table
print("\n[9] Events migration/schema")
out, _ = run("ls /var/www/somekorean/database/migrations/ 2>/dev/null | grep -i event")
print(out)
out, _ = run("grep -n 'event_date\\|date\\|time\\|column' /var/www/somekorean/database/migrations/*event* 2>/dev/null | head -20")
print(out)

# Check events error in detail
print("\n[10] Events 에러 상세")
out, _ = run("tail -200 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -B2 -A10 'event\\|Event' | head -80")
print(out[:3000])

client.close()
