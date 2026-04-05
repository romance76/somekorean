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

DB_HOST = db_config.get('DB_HOST', '127.0.0.1')
DB_NAME = db_config.get('DB_DATABASE', 'somekorean')
DB_USER = db_config.get('DB_USERNAME', 'root')
DB_PASS = db_config.get('DB_PASSWORD', '')

mycnf = f'[client]\nhost={DB_HOST}\nuser={DB_USER}\npassword={DB_PASS}\n'
enc = base64.b64encode(mycnf.encode()).decode()
ssh(f"echo '{enc}' | base64 -d > /tmp/fixall.cnf && chmod 600 /tmp/fixall.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode()).decode()
    ssh(f"echo '{enc}' | base64 -d > /tmp/fixall.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/fixall.cnf {DB_NAME} < /tmp/fixall.sql 2>&1")
    return out, err

# Get current columns
def get_columns(table):
    out, _ = mysql(f"SHOW COLUMNS FROM {table};")
    cols = set()
    for line in out.splitlines()[1:]:
        if '\t' in line:
            cols.add(line.split('\t')[0].strip())
    return cols

qa_cols = get_columns('qa_posts')
qaa_cols = get_columns('qa_answers')
recipe_cols = get_columns('recipe_posts')

log(f"qa_posts cols: {sorted(qa_cols)}")
log(f"qa_answers cols: {sorted(qaa_cols)}")
log(f"recipe_posts cols: {sorted(recipe_cols)}")

# Fix qa_posts - add all missing columns
qa_fixes = []
if 'view_count' not in qa_cols:
    qa_fixes.append("ADD COLUMN view_count INT NOT NULL DEFAULT 0")
if 'like_count' not in qa_cols:
    qa_fixes.append("ADD COLUMN like_count INT NOT NULL DEFAULT 0")
if 'is_pinned' not in qa_cols:
    qa_fixes.append("ADD COLUMN is_pinned TINYINT(1) NOT NULL DEFAULT 0")
if 'is_hidden' not in qa_cols:
    qa_fixes.append("ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0")

if qa_fixes:
    sql = f"ALTER TABLE qa_posts {', '.join(qa_fixes)};"
    out, err = mysql(sql)
    log(f"qa_posts fix: {out or 'ok'} {err or ''}")
else:
    log("qa_posts: no fixes needed")

# Fix qa_answers
qaa_fixes = []
if 'like_count' not in qaa_cols:
    qaa_fixes.append("ADD COLUMN like_count INT NOT NULL DEFAULT 0")
if 'is_hidden' not in qaa_cols:
    qaa_fixes.append("ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0")

if qaa_fixes:
    sql = f"ALTER TABLE qa_answers {', '.join(qaa_fixes)};"
    out, err = mysql(sql)
    log(f"qa_answers fix: {out or 'ok'} {err or ''}")
else:
    log("qa_answers: no fixes needed")

# Fix recipe_posts
recipe_fixes = []
if 'view_count' not in recipe_cols:
    recipe_fixes.append("ADD COLUMN view_count INT NOT NULL DEFAULT 0")
if 'like_count' not in recipe_cols:
    recipe_fixes.append("ADD COLUMN like_count INT NOT NULL DEFAULT 0")
if 'bookmark_count' not in recipe_cols:
    recipe_fixes.append("ADD COLUMN bookmark_count INT NOT NULL DEFAULT 0")
if 'is_hidden' not in recipe_cols:
    recipe_fixes.append("ADD COLUMN is_hidden TINYINT(1) NOT NULL DEFAULT 0")

if recipe_fixes:
    sql = f"ALTER TABLE recipe_posts {', '.join(recipe_fixes)};"
    out, err = mysql(sql)
    log(f"recipe_posts fix: {out or 'ok'} {err or ''}")
else:
    log("recipe_posts: no fixes needed")

# Verify
log("\n=== 검증 ===")
out, _ = mysql("SELECT id, title, is_hidden, view_count FROM qa_posts LIMIT 3;")
log("qa_posts test:\n" + out)

out, _ = mysql("SELECT id, title, is_hidden, view_count, like_count FROM recipe_posts LIMIT 3;")
log("recipe_posts test:\n" + out)

c.close()
log("Done!")
