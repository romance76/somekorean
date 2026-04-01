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

# ============================================================
# Step 1: EventController 소스 확인
# ============================================================
print("=" * 60)
print("EventController.php 라인 88-105 확인")
print("=" * 60)
out, _ = run("sed -n '85,110p' /var/www/somekorean/app/Http/Controllers/API/EventController.php")
print(out)

print("\n전체 파일 라인 수 확인")
out, _ = run("wc -l /var/www/somekorean/app/Http/Controllers/API/EventController.php")
print(out)

print("\njobs controller 확인")
out, _ = run("ls /var/www/somekorean/app/Http/Controllers/Api/ 2>/dev/null || ls /var/www/somekorean/app/Http/Controllers/API/ 2>/dev/null")
print(out)

print("\nJobs controller 경로 확인")
out, _ = run("find /var/www/somekorean/app/Http/Controllers -name '*Job*' 2>/dev/null")
print(out)

print("\nMarket controller 경로 확인")
out, _ = run("find /var/www/somekorean/app/Http/Controllers -name '*Market*' 2>/dev/null")
print(out)

# Store 메서드 필드 확인
print("\nJobs store 필드 확인")
out, _ = run("find /var/www/somekorean/app/Http/Controllers -name '*Job*' -exec grep -n 'validate\\|required\\|content\\|title' {} \\; 2>/dev/null | head -20")
print(out)

print("\nMarket store 필드 확인")
out, _ = run("find /var/www/somekorean/app/Http/Controllers -name '*Market*' -exec grep -n 'validate\\|required\\|content\\|title' {} \\; 2>/dev/null | head -20")
print(out)

# Job model
print("\nJobPost fillable 전체")
out, _ = run("grep -A20 'fillable' /var/www/somekorean/app/Models/JobPost.php 2>/dev/null")
print(out)

# Market model
print("\nMarket model fillable")
out, _ = run("find /var/www/somekorean/app/Models -name '*Market*' -exec grep -A15 'fillable' {} \\; 2>/dev/null")
print(out)

client.close()
print("\n진단 완료")
