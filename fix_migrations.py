#!/usr/bin/env python3
import paramiko, base64

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=20)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

# Read DB credentials from .env
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
print(f"DB: {DB_NAME} @ {DB_HOST} user={DB_USER}")

# Write .my.cnf
mycnf = f'[client]\nhost={DB_HOST}\nuser={DB_USER}\npassword={DB_PASS}\n'
encoded = base64.b64encode(mycnf.encode()).decode()
ssh(f"echo '{encoded}' | base64 -d > /tmp/fix_mig.cnf && chmod 600 /tmp/fix_mig.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode()).decode()
    ssh(f"echo '{enc}' | base64 -d > /tmp/fix_query.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/fix_mig.cnf {DB_NAME} < /tmp/fix_query.sql 2>&1")
    return out, err

# Get max batch
out, _ = mysql("SELECT MAX(batch) FROM migrations;")
print("Max batch output:", out)

batch = 21
for line in out.splitlines():
    try:
        v = int(line.strip())
        if v > 0:
            batch = v + 1
    except: pass
print(f"Using batch: {batch}")

# Insert migration records
sqls = [
    f"INSERT IGNORE INTO migrations (migration, batch) VALUES ('2026_03_29_000030_create_qa_tables', {batch});",
    f"INSERT IGNORE INTO migrations (migration, batch) VALUES ('2026_03_29_000031_create_recipe_tables', {batch});",
]

for sql in sqls:
    out, err = mysql(sql)
    print(f"SQL ok: {sql[:60]}... | {out} {err}")

# Verify migration status
out, _ = ssh("cd /var/www/somekorean && php artisan migrate:status 2>&1 | tail -6")
print("Migration status:\n", out)

c.close()
print("Done")
