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

out, _ = ssh("cat /var/www/somekorean/.env | grep -E '^DB_(HOST|DATABASE|USERNAME|PASSWORD)'")
db_config = {}
for line in out.splitlines():
    if '=' in line:
        k, v = line.split('=', 1)
        db_config[k.strip()] = v.strip().strip('"').strip("'")

DB_NAME = db_config.get('DB_DATABASE', 'somekorean')
DB_USER = db_config.get('DB_USERNAME', 'root')
DB_PASS = db_config.get('DB_PASSWORD', '')
DB_HOST = db_config.get('DB_HOST', '127.0.0.1')

mycnf = f'[client]\nhost={DB_HOST}\nuser={DB_USER}\npassword={DB_PASS}\n'
enc = base64.b64encode(mycnf.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/frm.cnf && chmod 600 /tmp/frm.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode()).decode()
    ssh(f"echo '{enc}' | base64 -d > /tmp/frm.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/frm.cnf {DB_NAME} < /tmp/frm.sql 2>&1")
    return out, err

# Check RecipeComment model
out, _ = ssh("cat /var/www/somekorean/app/Models/RecipeComment.php")
log("RecipeComment model:\n" + out)

# Create recipe_comments table with correct column name
sql = """CREATE TABLE IF NOT EXISTS recipe_comments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    rating TINYINT DEFAULT NULL,
    is_hidden TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
out, err = mysql(sql)
log(f"Create recipe_comments: {out or 'ok'} {err or ''}")

# Check
out, _ = mysql("SHOW TABLES LIKE 'recipe_comments';")
log("recipe_comments table exists: " + out)

# Now test the API
ssh("cd /var/www/somekorean && php artisan config:clear && php artisan route:clear && php artisan route:cache 2>&1")

out, _ = ssh("curl -sk https://somekorean.com/api/recipes/1 2>&1 | head -200")
log("\nRecipe detail API test:\n" + out[:800])

c.close()
log("Done!")
