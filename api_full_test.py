import paramiko
import json
import sys

hostname = '68.183.60.70'
username = 'root'
password = 'EhdRh0817wodl'

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTMwNzkyLCJleHAiOjE3NzQ5MzQzOTIsIm5iZiI6MTc3NDkzMDc5MiwianRpIjoicjhnTWVjdGdXMGI5YjhBTiIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.JD6QdqixWBkTYVPLyKxDo1146vv0mM--2aS_RWXxsAY"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, password=password, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def curl(method, path, data=None, auth=True):
    auth_hdr = f'-H "Authorization: Bearer {TOKEN}"' if auth else ''
    data_str = ''
    if data:
        data_json = json.dumps(data).replace("'", "'\\''")
        data_str = f"-H 'Content-Type: application/json' -d '{data_json}'"
    cmd = f'curl -s -X {method} {auth_hdr} {data_str} -w "\\nHTTP_STATUS:%{{http_code}}" https://somekorean.com/api{path}'
    out, err = run(cmd)
    lines = out.split('\n')
    status = ''
    body_lines = []
    for line in lines:
        if line.startswith('HTTP_STATUS:'):
            status = line.replace('HTTP_STATUS:', '')
        else:
            body_lines.append(line)
    return status, '\n'.join(body_lines)

results = []

def test(name, method, path, data=None, auth=True, expect_status=None):
    status, body = curl(method, path, data, auth)
    try:
        parsed = json.loads(body)
    except:
        parsed = None
    ok = True
    if expect_status:
        ok = status in expect_status
    elif status.startswith('4') or status.startswith('5'):
        ok = False
    results.append((name, ok, status, body[:200] if not ok else ''))
    return status, body, parsed

print("="*60)
print("=== Q&A TESTS ===")
print("="*60)

# Get fresh token first
fresh_token_php = r"""<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$u = App\Models\User::first();
echo auth('api')->login($u);
"""
sftp = client.open_sftp()
with sftp.open('/tmp/get_token2.php', 'w') as f:
    f.write(fresh_token_php)
sftp.close()
new_token_out, _ = run("php /tmp/get_token2.php 2>/dev/null")
new_token = new_token_out.strip()
if new_token and len(new_token) > 20:
    TOKEN = new_token
    print(f"Fresh token: {TOKEN[:50]}...")

# Q&A Tests
s, b, p = test('QA 카테고리 조회', 'GET', '/qa/categories', auth=False)
print(f"[QA-1] GET /qa/categories => HTTP {s}: {len(p) if isinstance(p,list) else 'N/A'} categories")

cats = p if isinstance(p, list) else []
cat_id = cats[0]['id'] if cats else 1

s, b, p = test('QA 목록 조회', 'GET', '/qa', auth=False)
print(f"[QA-2] GET /qa => HTTP {s}: {p.get('total','?') if p else 'N/A'} posts")

s, b, p = test('QA 질문 작성', 'POST', '/qa',
               data={'title': '한국어 테스트 질문', 'content': '테스트 내용입니다 답변 부탁드립니다', 'category_id': cat_id},
               expect_status=['201'])
print(f"[QA-3] POST /qa => HTTP {s}: id={p.get('id','?') if p else 'ERR'}")
qa_id = p.get('id') if p and isinstance(p, dict) else None

if not qa_id:
    s2, b2, p2 = test('QA 목록 재조회', 'GET', '/qa', auth=False)
    if p2 and 'data' in p2 and p2['data']:
        qa_id = p2['data'][0]['id']

s, b, p = test('QA 답변 작성', 'POST', f'/qa/{qa_id}/answers',
               data={'content': '테스트 답변입니다'},
               expect_status=['201'])
print(f"[QA-4] POST /qa/{qa_id}/answers => HTTP {s}: {p.get('message','?')[:50] if p else 'ERR'}")
ans_id = p.get('answer', {}).get('id') if p and isinstance(p.get('answer'), dict) else None

if qa_id and ans_id:
    s, b, p = test('QA 채택 답변', 'POST', f'/qa/{qa_id}/best-answer',
                   data={'answer_id': ans_id})
    print(f"[QA-5] POST /qa/{qa_id}/best-answer => HTTP {s}: {p.get('message','?')[:60] if p else 'ERR'}")

    s, b, p = test('QA 답변 좋아요', 'POST', f'/qa/answers/{ans_id}/like')
    print(f"[QA-6] POST /qa/answers/{ans_id}/like => HTTP {s}: likes={p.get('like_count','?') if p else 'ERR'}")

s, b, p = test('QA 검색', 'GET', '/qa?search=테스트', auth=False)
print(f"[QA-7] GET /qa?search=테스트 => HTTP {s}")

s, b, p = test('QA 카테고리 필터', 'GET', '/qa?status=open', auth=False)
print(f"[QA-8] GET /qa?status=open => HTTP {s}")

if qa_id:
    s, b, p = test('QA 상세 조회', 'GET', f'/qa/{qa_id}', auth=False)
    print(f"[QA-9] GET /qa/{qa_id} => HTTP {s}: answers={len(p.get('answers',[])) if p else '?'}")

print("\n" + "="*60)
print("=== GAME TESTS ===")
print("="*60)

s, b, p = test('게임 방 목록', 'GET', '/games/rooms', auth=False)
print(f"[GM-1] GET /games/rooms => HTTP {s}: {len(p) if isinstance(p,list) else 'N/A'} rooms")

s, b, p = test('게임 카테고리', 'GET', '/game-categories', auth=False)
print(f"[GM-2] GET /game-categories => HTTP {s}: {len(p) if isinstance(p,list) else 'N/A'} categories")
if isinstance(p, list):
    for c in p[:3]:
        name = c.get('name','?')
        sys.stdout.buffer.write(f"   - {name}\n".encode('utf-8', errors='replace'))

s, b, p = test('게임 방 생성', 'POST', '/games/rooms', data={'bet_points': 100, 'max_players': 2}, expect_status=['200','201'])
print(f"[GM-3] POST /games/rooms => HTTP {s}: id={p.get('id','?') if p else 'ERR'}")
room_id = p.get('id') if p and isinstance(p, dict) else None

if room_id:
    s, b, p = test('게임 방 상태', 'GET', f'/games/rooms/{room_id}/state')
    print(f"[GM-4] GET /games/rooms/{room_id}/state => HTTP {s}")

    s, b, p = test('게임 방 준비', 'POST', f'/games/rooms/{room_id}/ready')
    print(f"[GM-5] POST /games/rooms/{room_id}/ready => HTTP {s}: {p if p else 'ERR'}")

s, b, p = test('게임 리더보드', 'GET', '/games/leaderboard', auth=False)
print(f"[GM-6] GET /games/leaderboard => HTTP {s}")

s, b, p = test('내 게임 기록', 'GET', '/games/my-scores')
print(f"[GM-7] GET /games/my-scores => HTTP {s}: scores={len(p.get('scores',[])) if p else '?'}")

# Check which games exist
game_check_out, _ = run("mysql -u root -e \"SELECT id,name FROM somekorean.games LIMIT 5;\" 2>/dev/null || php /var/www/somekorean/artisan tinker --execute=\"echo DB::table('games')->limit(5)->get()->toJson();\" 2>/dev/null")
print(f"\n   [DB] Games: {game_check_out[:200]}")

s, b, p = test('게임 점수 저장', 'POST', '/games/1/score', data={'score': 1500, 'duration': 120, 'result': 'win', 'level': 1})
print(f"[GM-8] POST /games/1/score => HTTP {s}: {p.get('message','?') if p else b[:100]}")

s, b, p = test('게임 특정 리더보드', 'GET', '/games/1/leaderboard', auth=False)
print(f"[GM-9] GET /games/1/leaderboard => HTTP {s}")

s, b, p = test('게임 상점', 'GET', '/games/shop', auth=False)
print(f"[GM-10] GET /games/shop => HTTP {s}")

print("\n" + "="*60)
print("=== ELDER TESTS ===")
print("="*60)

s, b, p = test('Elder 설정 조회', 'GET', '/elder/settings')
print(f"[EL-1] GET /elder/settings => HTTP {s}: mode={p.get('elder_mode','?') if p else 'ERR'}")

s, b, p = test('Elder 설정 업데이트', 'PUT', '/elder/settings',
               data={'elder_mode': True, 'checkin_interval': 24, 'guardian_phone': '010-1234-5678', 'guardian_name': 'Test Guardian'})
print(f"[EL-2] PUT /elder/settings => HTTP {s}: guardian={p.get('guardian_name','?') if p else 'ERR'}")

s, b, p = test('Elder 체크인', 'POST', '/elder/checkin')
print(f"[EL-3] POST /elder/checkin => HTTP {s}: {p.get('message','?')[:60] if p else b[:100]}")

s, b, p = test('Elder 보호자 조회', 'GET', '/elder/guardian/1')
print(f"[EL-4] GET /elder/guardian/1 => HTTP {s}: {str(p)[:100] if p else b[:100]}")

s, b, p = test('Elder SOS', 'POST', '/elder/sos', data={'message': 'Test emergency', 'lat': 34.0522, 'lng': -118.2437})
print(f"[EL-5] POST /elder/sos => HTTP {s}: {p.get('message','?')[:60] if p else b[:100]}")

print("\n" + "="*60)
print("=== RIDE TESTS ===")
print("="*60)

# Check DriverProfile model/table
dp_check, _ = run("grep -r 'DriverProfile' /var/www/somekorean/app/ 2>/dev/null | head -5")
print(f"   [DEBUG] DriverProfile refs: {dp_check[:200]}")

s, b, p = test('라이드 요청', 'POST', '/ride/request', data={
    'pickup_address': 'Test Pickup Address',
    'destination_address': 'Test Destination',
    'pickup_lat': 34.0522, 'pickup_lng': -118.2437,
    'dest_lat': 34.0622, 'dest_lng': -118.2537,
    'notes': 'Test'
}, expect_status=['200', '201'])
print(f"[RD-1] POST /ride/request => HTTP {s}: id={p.get('id','?') if p else b[:100]}")
ride_id = p.get('id') if p and isinstance(p, dict) else None

s, b, p = test('라이드 주변 조회', 'GET', '/ride/nearby?lat=34.0522&lng=-118.2437', auth=True)
print(f"[RD-2] GET /ride/nearby => HTTP {s}: {len(p) if isinstance(p,list) else str(p)[:80]}")

s, b, p = test('라이드 히스토리', 'GET', '/ride/history')
print(f"[RD-3] GET /ride/history => HTTP {s}: {len(p) if isinstance(p,list) else str(p)[:80]}")

if ride_id:
    s, b, p = test('라이드 상세', 'GET', f'/ride/{ride_id}')
    print(f"[RD-4] GET /ride/{ride_id} => HTTP {s}: status={p.get('status','?') if p else 'ERR'}")

    s, b, p = test('라이드 취소', 'POST', f'/ride/{ride_id}/cancel')
    print(f"[RD-5] POST /ride/{ride_id}/cancel => HTTP {s}: {p.get('message','?')[:60] if p else b[:100]}")

client.close()

print("\n" + "="*60)
print("=== FINAL SUMMARY ===")
print("="*60)
passed = sum(1 for _, ok, _, _ in results if ok)
failed = sum(1 for _, ok, _, _ in results if not ok)
for name, ok, status, detail in results:
    icon = "PASS" if ok else "FAIL"
    extra = f" => {detail}" if detail else ""
    print(f"[{icon}] {name} (HTTP {status}){extra}")

print(f"\nTotal: {passed} PASS / {failed} FAIL / {len(results)} tests")
