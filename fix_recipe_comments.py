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
ssh(f"echo '{enc}' | base64 -d > /tmp/frc.cnf && chmod 600 /tmp/frc.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode()).decode()
    ssh(f"echo '{enc}' | base64 -d > /tmp/frc.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/frc.cnf {DB_NAME} < /tmp/frc.sql 2>&1")
    return out, err

# Check if recipe_comments exists
out, _ = mysql("SHOW TABLES LIKE 'recipe_comments';")
log("recipe_comments table: " + out)

if not out.strip() or 'recipe_comments' not in out:
    # Create table
    log("Creating recipe_comments table...")
    sql = """CREATE TABLE IF NOT EXISTS recipe_comments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recipe_post_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    rating TINYINT DEFAULT NULL,
    is_hidden TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    FOREIGN KEY (recipe_post_id) REFERENCES recipe_posts(id) ON DELETE CASCADE
);"""
    out, err = mysql(sql)
    log(f"Create result: {out or 'ok'} {err or ''}")
else:
    out, _ = mysql("DESCRIBE recipe_comments;")
    log("recipe_comments columns:\n" + out)

# Check RecipePost model relationship
out, _ = ssh("cat /var/www/somekorean/app/Models/RecipePost.php")
log("\nRecipePost model:\n" + out[:2000])

# Enable debug and check error
ssh("cd /var/www/somekorean && sed -i 's/APP_DEBUG=false/APP_DEBUG=true/' .env && php artisan config:clear 2>/dev/null")
out, _ = ssh("curl -sk https://somekorean.com/api/recipes/1 2>&1")
# Restore
ssh("cd /var/www/somekorean && sed -i 's/APP_DEBUG=true/APP_DEBUG=false/' .env && php artisan config:clear 2>/dev/null")
log("\nRecipe detail debug response:\n" + out[:1500])

c.close()
