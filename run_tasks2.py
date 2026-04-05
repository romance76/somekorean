import paramiko, base64, sys, time, random
from datetime import datetime, timedelta

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

env_out, _ = ssh('cat /var/www/somekorean/.env | grep -E "^DB_"')
db_config = {}
for line in env_out.splitlines():
    if '=' in line:
        k, v = line.split('=', 1)
        db_config[k.strip()] = v.strip().strip('"').strip("'")

DB_NAME = db_config.get('DB_DATABASE', 'somekorean')
DB_USER = db_config.get('DB_USERNAME', 'root')
DB_PASS = db_config.get('DB_PASSWORD', '')
DB_HOST = db_config.get('DB_HOST', '127.0.0.1')

mycnf = f'[client]\nhost={DB_HOST}\nuser={DB_USER}\npassword={DB_PASS}\n'
enc = base64.b64encode(mycnf.encode('utf-8')).decode('ascii')
ssh(f"echo '{enc}' | base64 -d > /tmp/sk_main.cnf && chmod 600 /tmp/sk_main.cnf")

def mysql(sql):
    enc = base64.b64encode(sql.encode('utf-8')).decode('ascii')
    ssh(f"echo '{enc}' | base64 -d > /tmp/sk_main.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf {DB_NAME} < /tmp/sk_main.sql 2>&1")
    return out

# TASK 6: Add fake recipe comments
print("\n=== TASK 6: Add fake recipe comments ===")

# Get recipe user map
result = mysql("SELECT id, user_id FROM recipe_posts ORDER BY id LIMIT 150;")
recipe_user_map = {}
for line in result.splitlines()[1:]:
    parts = line.split('\t')
    if len(parts) >= 2:
        try:
            rid = int(parts[0].strip())
            ruid = int(parts[1].strip())
            recipe_user_map[rid] = ruid
        except:
            pass

print(f"Recipe user map size: {len(recipe_user_map)}")

# Get fake user ids
result = mysql("SELECT id FROM users WHERE id >= 53 ORDER BY id;")
fake_user_ids = []
for line in result.splitlines()[1:]:
    line = line.strip()
    if line.isdigit():
        fake_user_ids.append(int(line))

print(f"Fake users: {len(fake_user_ids)}")

comments_templates = [
    '정말 맛있어요! 가족들이 너무 좋아했어요',
    '미국 마트에서 재료 구하기 쉬워서 자주 만들어요',
    '처음 해봤는데 성공했어요! 설명이 자세해요',
    '조금 매울 수 있으니 고추장 양 조절하세요',
    '아이들이 너무 잘 먹어요. 강추!',
    '한국 음식 그리울 때 이걸로 해결해요',
    'Walmart에서 다 구했어요!',
    '양념 비율이 딱 맞아요. 레스토랑 맛이에요',
    '쉽고 빠르게 만들 수 있어서 좋아요',
    '남편이 반해버렸어요 ㅎㅎ',
    '이 레시피 덕분에 요리 실력 늘었어요',
    'H-Mart 재료로 완성! 너무 맛있어요',
    '포인트가 있어서 따라하기 쉬워요',
    '저처럼 초보도 할 수 있어요!',
    '다음엔 두 배로 만들어야겠어요'
]

# Build all insert values
all_rows = []
base_date = datetime.now()

random.seed(42)
for i, (rid, ruid) in enumerate(recipe_user_map.items()):
    num_comments = random.randint(2, 4)
    for j in range(num_comments):
        # Pick a user different from recipe author
        available_users = [u for u in fake_user_ids if u != ruid]
        if not available_users:
            available_users = fake_user_ids
        uid = available_users[(i * 7 + j * 13) % len(available_users)]

        content = comments_templates[(i * 3 + j * 5) % len(comments_templates)]
        content = content.replace("'", "''")  # SQL escape

        rating = 3 + (i + j) % 3  # 3, 4, or 5
        days_ago = (i * 3 + j * 11) % 180
        created_at = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

        all_rows.append(f"({rid}, {uid}, '{content}', {rating}, 0, '{created_at}', '{created_at}')")

print(f"Total comment rows to insert: {len(all_rows)}")

# Insert in batches of 10
batch_size = 10
errors = 0
inserted = 0
for start in range(0, len(all_rows), batch_size):
    batch = all_rows[start:start+batch_size]
    sql = "INSERT INTO recipe_comments (recipe_id, user_id, content, rating, is_hidden, created_at, updated_at) VALUES " + ',\n'.join(batch) + ";"
    result = mysql(sql)
    if result and 'ERROR' in result:
        print(f"Batch error at {start}: {result[:200]}")
        errors += 1
    else:
        inserted += len(batch)

print(f"Inserted {inserted} comments, {errors} errors")

result = mysql("SELECT COUNT(*) FROM recipe_comments;")
print("Total recipe_comments now:", result)

# TASK 7: Update recipe stats
print("\n=== TASK 7: Update recipe stats ===")
sql = """UPDATE recipe_posts SET view_count = 50 + (id * 13 % 2000), like_count = 5 + (id * 7 % 200), bookmark_count = 1 + (id * 3 % 50) WHERE view_count = 0 OR view_count IS NULL;"""
result = mysql(sql)
print("Recipe stats update:", result or "OK")

result = mysql("SELECT COUNT(*) FROM recipe_posts WHERE view_count > 0;")
print("Recipes with view_count:", result)

print("\n=== Tasks 6 and 7 complete ===")
