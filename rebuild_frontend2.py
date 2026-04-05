#!/usr/bin/env python3
import paramiko, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=180):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

log("=== Vite 빌드 시작 ===")
out, err = ssh("cd /var/www/somekorean && npm run build 2>&1", timeout=300)
# Show last 2000 chars
output = out + err
log(output[-3000:] if len(output) > 3000 else output)

log("\n=== 캐시 초기화 ===")
out, err = ssh("cd /var/www/somekorean && php artisan cache:clear && php artisan config:clear && php artisan route:clear && php artisan view:clear 2>&1")
log(out)

log("\n=== 라우트 캐시 ===")
out, err = ssh("cd /var/www/somekorean && php artisan route:cache 2>&1")
log(out)

log("\n=== Q&A API 테스트 ===")
out, err = ssh("curl -s http://localhost/api/qa/categories 2>&1")
log(out[:500])

log("\n=== 레시피 API 테스트 ===")
out, err = ssh("curl -s http://localhost/api/recipes/categories 2>&1")
log(out[:500])

log("\n=== DB 카운트 확인 (config file 방식) ===")
import base64
mycnf_enc = base64.b64encode(b'[client]\nhost=127.0.0.1\nuser=somekorean_user\npassword=EhdRh0817wodl\n').decode()
ssh(f"echo '{mycnf_enc}' | base64 -d > /tmp/check.cnf && chmod 600 /tmp/check.cnf")

sq = "SELECT 'qa_posts', COUNT(*) FROM qa_posts UNION SELECT 'recipe_posts', COUNT(*) FROM recipe_posts;"
enc = base64.b64encode(sq.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/check.sql")
out, err = ssh("mysql --defaults-file=/tmp/check.cnf somekorean < /tmp/check.sql 2>&1")
log(out)

c.close()
log("\nDone!")
