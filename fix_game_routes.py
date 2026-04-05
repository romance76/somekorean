import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=180):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()
def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# Show all games
print("=== 전체 게임 목록 ===")
all_games = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT id, name, slug, route_name FROM games ORDER BY id;\"")
print(all_games)

# Fix route names by ID
print("\n=== DB 라우트 수정 ===")
route_fixes = [
    (1, 'game-hangul'),       # 한글 자음모음 퍼즐
    (2, 'game-alphabet'),     # 영어 알파벳 퍼즐 (need to create)
    (3, 'game-counting'),     # 숫자 세기
    (12, 'game-multiplication'),  # 구구단
    (13, 'game-wordblank'),   # 한국어 단어 맞추기
    (16, 'game-engcard'),     # 영어 단어 카드
    (23, 'game-coding-quiz'), # 코딩 퀴즈 (was tower defense)
]
for gid, route in route_fixes:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE id={gid};\"")
    print(f"ID {gid} -> {route}: {r or 'OK'}")

# Check which route names still need Vue files
print("\n=== 라우터에 없는 라우트 확인 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
print("Router has game-alphabet?", 'game-alphabet' in router_content)
print("Router has game-multiplication?", 'game-multiplication' in router_content)

# Games 31-47 status
print("\n=== 게임 31-47 현황 ===")
rest_games = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT id, name, route_name FROM games WHERE id >= 31 ORDER BY id;\"")
print(rest_games)
