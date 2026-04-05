import paramiko, base64, sys, time, random

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# Get DB config
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

def mysql(sql, verbose=True):
    enc = base64.b64encode(sql.encode('utf-8')).decode('ascii')
    ssh(f"echo '{enc}' | base64 -d > /tmp/sk_main.sql")
    out, err = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf {DB_NAME} < /tmp/sk_main.sql 2>&1")
    return out

# TASK 1: Add nickname column
print("\n=== TASK 1: Add nickname column ===")
check = mysql("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='nickname';")
col_exists = check.strip().split('\n')[-1].strip() if check else '0'
print(f"Column exists check: {col_exists}")
if col_exists == '0':
    result = mysql("ALTER TABLE users ADD COLUMN nickname VARCHAR(50) NULL AFTER username;")
    print("Added nickname column:", result or "OK")
else:
    print("Nickname column already exists, skipping")

# TASK 2: Set nicknames for fake users
print("\n=== TASK 2: Set nicknames for fake users ===")
result = mysql("SELECT id FROM users WHERE id >= 53 ORDER BY id;")
user_ids = []
for line in result.splitlines()[1:]:
    line = line.strip()
    if line.isdigit():
        user_ids.append(int(line))
print(f"Found {len(user_ids)} fake users")

nicknames = [
    '미국한인생활', '한국사랑해', '조지아주한인', '텍사스한국인', '뉴욕한인',
    '캘리포니아꿈', '시카고한인', '플로리다한국', '시애틀비하인드', '보스턴유학생',
    '라스베가스한인', '샌프란시스코꿈', '마이애미한국', '달라스한인회', '애틀랜타한인',
    '워싱턴DC한인', '피닉스사막한인', '덴버하이킹족', '포틀랜드커피', '내쉬빌음악한인',
    '미네소타추위', '오하이오한인', '버지니아직장인', '뉴저지한국타운', '필라델피아한인',
    '찰스턴한인', '새크라멘토사과', '산호세테크', '오스틴스타트업', '탬파베이한인',
    '콜럼버스한국', '인디아나폴리스', '멤피스블루스', '루이빌한인', '오클라호마한인',
    '알버커키한인', '툭슨한인', '리치먼드한국', '하트퍼드한인', '프로비던스한인',
    '버팔로한인', '로체스터한국', '앨버니한인', '사바나한인', '모빌한인',
    '잭슨빌한인', '올랜도한인', '멜번한인', '탬파한인', '클리블랜드한인',
    '피츠버그한인', '밀워키한인', '미니애폴리스', '캔자스시티한인', '세인트루이스',
    '솔트레이크한인', '보이시한인', '앵커리지한인', '호놀룰루한인', '랄리한인',
    '샬럿한인', '그린즈버러', '더럼한인', '윌밍턴한인', '아이오와한인',
    '매디슨한인', '링컨한인', '오마하한인', '그린베이한인', '스포케인한인',
    '탈컴한인', '유진한인', '코르발리스한인', '사이살렘한인', '메드퍼드한인',
    '아스토리아한인', '고스포켓', '핫도그킹', '비빔밥마스터'
]

batch_sqls = []
current_batch = []
for i, uid in enumerate(user_ids):
    nick = nicknames[i % len(nicknames)]
    current_batch.append(f"UPDATE users SET nickname = '{nick}' WHERE id = {uid};")
    if len(current_batch) >= 20:
        batch_sqls.append('\n'.join(current_batch))
        current_batch = []
if current_batch:
    batch_sqls.append('\n'.join(current_batch))

print(f"Running {len(batch_sqls)} batches...")
errors = 0
for i, sql in enumerate(batch_sqls):
    result = mysql(sql)
    if result and 'ERROR' in result:
        print(f"Batch {i+1} error: {result}")
        errors += 1
    else:
        print(f"Batch {i+1}/{len(batch_sqls)} OK")

result = mysql("SELECT id, nickname FROM users WHERE id >= 53 LIMIT 5;")
print("Sample nicknames:", result)

print("\n=== TASK 3: Randomize Q&A post user assignments ===")
result = mysql("SELECT MIN(id), MAX(id), COUNT(*) FROM users WHERE id >= 53;")
print("Fake user range:", result)

result = mysql("SELECT COUNT(*) FROM qa_posts;")
print("Total qa_posts:", result)

result = mysql("SELECT MIN(id), MAX(id) FROM users WHERE id >= 53;")
lines = result.splitlines()
if len(lines) >= 2:
    parts = lines[1].split('\t')
    min_uid = int(parts[0].strip()) if parts[0].strip().isdigit() else 53
    max_uid = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 272
else:
    min_uid, max_uid = 53, 272

range_size = max_uid - min_uid + 1
print(f"User ID range: {min_uid}-{max_uid}, size: {range_size}")

sql = f"UPDATE qa_posts SET user_id = {min_uid} + (id % {range_size});"
result = mysql(sql)
print("qa_posts update result:", result or "OK")

result = mysql("SELECT COUNT(DISTINCT user_id) FROM qa_posts;")
print("Distinct user_ids in qa_posts:", result)

print("\n=== TASK 4: Randomize Q&A answer user assignments ===")
range_size2 = max_uid - min_uid
sql = f"UPDATE qa_answers SET user_id = {min_uid + 1} + (id % {range_size2});"
result = mysql(sql)
print("qa_answers update result:", result or "OK")

result = mysql("SELECT COUNT(DISTINCT user_id) FROM qa_answers;")
print("Distinct user_ids in qa_answers:", result)

print("\n=== TASK 5: Randomize Q&A stats ===")
sql = """UPDATE qa_posts SET view_count = 10 + (id * 7 % 500), like_count = id % 20, answer_count = (SELECT COUNT(*) FROM qa_answers WHERE qa_post_id = qa_posts.id);"""
result = mysql(sql)
print("qa_posts stats update:", result or "OK")

sql = """UPDATE qa_posts p SET best_answer_id = (SELECT id FROM qa_answers WHERE qa_post_id = p.id ORDER BY id LIMIT 1), status = 'solved' WHERE (p.id % 3 = 0) AND EXISTS (SELECT 1 FROM qa_answers WHERE qa_post_id = p.id);"""
result = mysql(sql)
print("best_answer update:", result or "OK")

result = mysql("SELECT COUNT(*) FROM qa_posts WHERE status='solved';")
print("Solved posts:", result)

print("\n=== TASK 6: Check recipe comments ===")
result = mysql("SELECT COUNT(*) FROM recipe_comments;")
print("Current recipe comments count:", result)

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

# Check recipe_comments table structure
result = mysql("DESCRIBE recipe_comments;")
print("recipe_comments schema:", result)

print("\nScript part 1 complete")
