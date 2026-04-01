#!/usr/bin/env python3
import paramiko, sys, base64

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=30):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip(), stderr.read().decode('utf-8', errors='replace').strip()

# Check actual domain
out, _ = ssh("cat /etc/nginx/sites-enabled/* | grep server_name | head -5")
log("Server names: " + out)

# Check if using domain or IP
out, _ = ssh("curl -s -o /dev/null -w '%{http_code}' http://68.183.60.70/api/qa/categories")
log("QA API via IP: " + out)

out, _ = ssh("curl -s http://68.183.60.70/api/qa/categories 2>&1 | head -200")
log("QA API response: " + out[:500])

# Check route list
out, _ = ssh("cd /var/www/somekorean && php artisan route:list --path=api/qa 2>&1 | head -20")
log("QA Routes:\n" + out)

out, _ = ssh("cd /var/www/somekorean && php artisan route:list --path=api/recipes 2>&1 | head -20")
log("Recipe Routes:\n" + out)

# Check DB password from .env
out, _ = ssh("cat /var/www/somekorean/.env | grep DB_PASSWORD")
log("DB pass: " + out)

# DB count with correct password
out2, _ = ssh("cat /var/www/somekorean/.env | grep -E '^DB_PASSWORD'")
db_pass = out2.split('=', 1)[1].strip().strip('"').strip("'") if '=' in out2 else ''
log(f"DB password found: {'yes' if db_pass else 'no'}")

mycnf = f'[client]\nhost=127.0.0.1\nuser=somekorean_user\npassword={db_pass}\n'
enc = base64.b64encode(mycnf.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/chk2.cnf && chmod 600 /tmp/chk2.cnf")

sq = "SELECT 'qa_posts', COUNT(*) FROM qa_posts UNION SELECT 'recipe_posts', COUNT(*) FROM recipe_posts;"
enc2 = base64.b64encode(sq.encode()).decode()
ssh(f"echo '{enc2}' | base64 -d > /tmp/chk2.sql")
out3, err3 = ssh("mysql --defaults-file=/tmp/chk2.cnf somekorean < /tmp/chk2.sql 2>&1")
log("DB counts:\n" + out3 + ("\n" + err3 if err3 else ""))

c.close()
log("Done!")
