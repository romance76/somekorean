#!/usr/bin/env python3
import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

print("=== Vite 빌드 ===")
out, err = ssh("cd /var/www/somekorean && npm run build 2>&1", timeout=180)
print(out[-2000:] if len(out) > 2000 else out)
if err:
    print("STDERR:", err[-500:])

print("\n=== 캐시 초기화 ===")
out, err = ssh("cd /var/www/somekorean && php artisan cache:clear && php artisan config:clear && php artisan route:clear && php artisan view:clear 2>&1")
print(out)
if err:
    print("STDERR:", err)

print("\n=== 라우트 캐시 ===")
out, err = ssh("cd /var/www/somekorean && php artisan route:cache 2>&1")
print(out)

print("\n=== Q&A API 테스트 ===")
out, err = ssh("curl -s http://localhost/api/qa/categories 2>&1 | head -200")
print(out[:500])

print("\n=== 레시피 API 테스트 ===")
out, err = ssh("curl -s http://localhost/api/recipes/categories 2>&1 | head -200")
print(out[:500])

print("\n=== DB 확인 ===")
out, err = ssh("cd /var/www/somekorean && php artisan tinker --execute \"echo json_encode(['qa'=>\\DB::table('qa_posts')->count(), 'recipes'=>\\DB::table('recipe_posts')->count()])\" 2>&1")
print(out)

c.close()
print("\nDone!")
