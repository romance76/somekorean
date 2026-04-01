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

# Get DB credentials
out, _ = ssh("cat /var/www/somekorean/.env | grep -E '^DB_(HOST|DATABASE|USERNAME|PASSWORD)'")
db_config = {}
for line in out.splitlines():
    if '=' in line:
        k, v = line.split('=', 1)
        db_config[k.strip()] = v.strip().strip('"').strip("'")

DB_HOST = db_config.get('DB_HOST', '127.0.0.1')
DB_NAME = db_config.get('DB_DATABASE', 'somekorean')
DB_USER = db_config.get('DB_USERNAME', 'root')
DB_PASS = db_config.get('DB_PASSWORD', '')

mycnf = f'[client]\nhost={DB_HOST}\nuser={DB_USER}\npassword={DB_PASS}\n'
enc = base64.b64encode(mycnf.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/fix2.cnf && chmod 600 /tmp/fix2.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode()).decode()
    ssh(f"echo '{enc}' | base64 -d > /tmp/fix2.sql")
    out, err = ssh("mysql --defaults-file=/tmp/fix2.cnf " + DB_NAME + " < /tmp/fix2.sql 2>&1")
    return out, err

# Check qa_posts columns
out, err = mysql("DESCRIBE qa_posts;")
log("qa_posts columns:\n" + out)

out, err = mysql("DESCRIBE qa_answers;")
log("\nqa_answers columns:\n" + out)

out, err = mysql("DESCRIBE recipe_posts;")
log("\nrecipe_posts columns:\n" + out)

# Add missing columns if they don't exist
fixes = []

# Check is_hidden in qa_posts
if 'is_hidden' not in out[:1000]:
    out2, _ = mysql("DESCRIBE qa_posts;")
    if 'is_hidden' not in out2:
        fixes.append(("qa_posts is_hidden", "ALTER TABLE qa_posts ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0 AFTER is_pinned;"))

# Check is_hidden in qa_answers
out3, _ = mysql("DESCRIBE qa_answers;")
if 'is_hidden' not in out3:
    fixes.append(("qa_answers is_hidden", "ALTER TABLE qa_answers ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0;"))

# Check is_hidden in recipe_posts
out4, _ = mysql("DESCRIBE recipe_posts;")
if 'is_hidden' not in out4:
    fixes.append(("recipe_posts is_hidden", "ALTER TABLE recipe_posts ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0;"))

# Apply fixes
for name, sql in fixes:
    out, err = mysql(sql)
    log(f"Fix {name}: {out or 'ok'} {err or ''}")

# Test the API query
out, err = mysql("SELECT id, title FROM qa_posts WHERE is_hidden = 0 LIMIT 3;")
log("\nQuery test (qa_posts):\n" + out)

out, err = mysql("SELECT id, title FROM recipe_posts WHERE is_hidden = 0 LIMIT 3;")
log("\nQuery test (recipe_posts):\n" + out)

c.close()
log("\nDone!")
