import paramiko
import os
import sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:80]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:400]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Demo Seed Re-run ===')

# ── 1. Upload fixed DemoDataSeeder ────────────────────────────────────────────
print('\n[1] Uploading fixed DemoDataSeeder.php...')
upload(
    os.path.join(LOCAL, 'database', 'seeders', 'DemoDataSeeder.php'),
    f'{APP}/database/seeders/DemoDataSeeder.php'
)

# ── 2. Truncate demo data tables (keep admin users id=1,2) ───────────────────
print('\n[2] Truncating partial demo data...')
run(f'''mysql -u somekorean_user -p'SK_DB@2026!secure' somekorean -e "
SET FOREIGN_KEY_CHECKS=0;
DELETE FROM business_reviews;
DELETE FROM businesses;
DELETE FROM chat_messages;
DELETE FROM comments;
DELETE FROM job_posts;
DELETE FROM market_items;
DELETE FROM point_logs WHERE user_id > 2;
DELETE FROM posts;
DELETE FROM quiz_attempts;
DELETE FROM quiz_questions WHERE id > 10;
DELETE FROM users WHERE id > 2;
SET FOREIGN_KEY_CHECKS=1;
" 2>/dev/null''')

# ── 3. Run seeder ─────────────────────────────────────────────────────────────
print('\n[3] Running DemoDataSeeder...')
run(f'cd {APP} && php8.2 artisan db:seed --class=DemoDataSeeder --force 2>&1', timeout=240)

# ── 4. DB counts ─────────────────────────────────────────────────────────────
print('\n[4] DB counts after seeding...')
run(f'''mysql -u somekorean_user -p'SK_DB@2026!secure' somekorean -e "
SELECT 'users' AS tbl, COUNT(*) AS cnt FROM users
UNION SELECT 'posts', COUNT(*) FROM posts
UNION SELECT 'comments', COUNT(*) FROM comments
UNION SELECT 'job_posts', COUNT(*) FROM job_posts
UNION SELECT 'market_items', COUNT(*) FROM market_items
UNION SELECT 'businesses', COUNT(*) FROM businesses
UNION SELECT 'business_reviews', COUNT(*) FROM business_reviews
UNION SELECT 'quiz_questions', COUNT(*) FROM quiz_questions
UNION SELECT 'chat_rooms', COUNT(*) FROM chat_rooms
UNION SELECT 'chat_messages', COUNT(*) FROM chat_messages;
" 2>/dev/null''')

# ── 5. Final site check ───────────────────────────────────────────────────────
print('\n[5] Final site check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Seed Re-run DONE ===')
