import requests
import json
import sys

BASE_URL = "https://somekorean.com/api"

# 토큰 생성 함수
def get_token():
    import paramiko
    import base64
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
    cmd = r"""cat > /tmp/get_token.php << 'HEREDOC'
<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$u = App\Models\User::first();
$token = auth('api')->login($u);
echo "TOKEN:" . $token;
HEREDOC"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/somekorean && php /tmp/get_token.php 2>/dev/null')
    result = stdout.read().decode().strip()
    ssh.close()
    if 'TOKEN:' in result:
        return result.split('TOKEN:')[1].strip()
    return None

TOKEN = get_token()
print(f"Token: {TOKEN[:50]}...")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

results = []

def test(name, method, url, data=None, expected_status=200):
    try:
        full_url = BASE_URL + url
        if method == 'GET':
            r = requests.get(full_url, headers=HEADERS, timeout=15)
        elif method == 'POST':
            r = requests.post(full_url, headers=HEADERS, json=data, timeout=15)
        elif method == 'PUT':
            r = requests.put(full_url, headers=HEADERS, json=data, timeout=15)
        elif method == 'DELETE':
            r = requests.delete(full_url, headers=HEADERS, timeout=15)

        status = r.status_code
        try:
            body = r.json()
        except:
            body = r.text[:300]

        passed = (status == expected_status) or (expected_status == 200 and status in [200, 201])
        result = "PASS" if passed else "FAIL"
        results.append({
            "name": name,
            "result": result,
            "status": status,
            "body_preview": str(body)[:300]
        })
        print(f"[{result}] {name} - HTTP {status}")
        if not passed:
            print(f"  Response: {str(body)[:400]}")
        return status, body
    except Exception as e:
        results.append({"name": name, "result": "FAIL", "status": "ERROR", "body_preview": str(e)})
        print(f"[FAIL] {name} - ERROR: {e}")
        return None, None

print("\n" + "=" * 60)
print("이벤트 기능 테스트")
print("=" * 60)

# 1. 이벤트 목록
status, body = test("이벤트 목록 GET /events", "GET", "/events")
event_list = body.get('data', []) if isinstance(body, dict) else []
print(f"  Events count: {len(event_list)}")

# 2. 날짜 필터
test("이벤트 날짜 필터", "GET", "/events?start_date=2026-01-01&end_date=2026-12-31")

# 3. 카테고리 필터
test("이벤트 카테고리 필터", "GET", "/events?category=social")

# 4. 검색
test("이벤트 검색", "GET", "/events?search=Korean")

# 5. 이벤트 등록 (category: social 포함)
event_data = {
    "title": "테스트 이벤트 2026",
    "description": "테스트 설명입니다",
    "event_date": "2026-06-15 14:00:00",
    "location": "뉴욕 한인회관",
    "category": "social",
    "max_attendees": 50,
    "price": 0,
    "region": "NY",
    "is_online": False
}
status, body = test("이벤트 등록 POST /events (category=social)", "POST", "/events", event_data, 201)
event_id = None
if isinstance(body, dict):
    event_id = body.get('id') or body.get('data', {}).get('id')
    print(f"  Created event_id: {event_id}")

# event_date 없이 등록 (422 예상)
test("이벤트 등록 (event_date 없음) - 422 예상", "POST", "/events",
     {"title": "날짜없는 이벤트", "description": "테스트"}, 422)

# 기존 published 이벤트로 테스트
published_id = event_list[0]['id'] if event_list else None
if published_id:
    # 6. 이벤트 상세
    status, body = test(f"이벤트 상세 GET /events/{published_id}", "GET", f"/events/{published_id}")

    # 7. 이벤트 참가신청 (published 이벤트)
    status, body = test(f"이벤트 참가신청 (published) POST /events/{published_id}/attend", "POST", f"/events/{published_id}/attend")
    print(f"  Attend response: {str(body)[:200]}")

    # 8. 북마크
    status, body = test(f"이벤트 북마크 POST /events/{published_id}/bookmark", "POST", f"/events/{published_id}/bookmark")
    print(f"  Bookmark response: {str(body)[:200]}")

    # 9. 좋아요
    status, body = test(f"이벤트 좋아요 POST /events/{published_id}/like", "POST", f"/events/{published_id}/like")
    print(f"  Like response: {str(body)[:200]}")

if event_id:
    # 10. 이벤트 수정
    test(f"이벤트 수정 PUT /events/{event_id}", "PUT", f"/events/{event_id}", {
        "title": "수정된 테스트 이벤트",
        "event_date": "2026-07-20 14:00:00"
    })

    # 11. 이벤트 삭제
    test(f"이벤트 삭제 DELETE /events/{event_id}", "DELETE", f"/events/{event_id}")

print()
print("=" * 60)
print("동호회 기능 테스트")
print("=" * 60)

# 동호회 목록
status, body = test("동호회 목록 GET /clubs", "GET", "/clubs")
club_list = body.get('data', []) if isinstance(body, dict) else []
print(f"  Clubs count: {len(club_list)}")

# 동호회 생성
club_data = {
    "name": "테스트 동호회 2026",
    "description": "테스트 동호회입니다",
    "category": "스포츠",
    "region": "뉴욕",
    "is_approval": False
}
status, body = test("동호회 생성 POST /clubs", "POST", "/clubs", club_data, 201)
new_club_id = None
if isinstance(body, dict):
    new_club_id = body.get('club', {}).get('id') or body.get('id') or body.get('data', {}).get('id')
    print(f"  Created club_id: {new_club_id}")

# 기존 동호회로 테스트
existing_club_id = club_list[0]['id'] if club_list else None

if existing_club_id:
    # 동호회 상세
    test(f"동호회 상세 GET /clubs/{existing_club_id}", "GET", f"/clubs/{existing_club_id}")

    # 동호회 게시판 (GET)
    status, body = test(f"동호회 게시판 GET /clubs/{existing_club_id}/posts", "GET", f"/clubs/{existing_club_id}/posts")
    print(f"  Posts response: {str(body)[:200]}")

if new_club_id:
    # 동호회 게시글 작성 (생성자는 owner, 즉 approved member)
    post_data = {"title": "테스트 게시글", "content": "테스트 내용입니다"}
    status, body = test(f"동호회 게시글 작성 POST /clubs/{new_club_id}/posts", "POST", f"/clubs/{new_club_id}/posts", post_data, 201)
    print(f"  Post create response: {str(body)[:300]}")

    # 다른 클럽에서 탈퇴 테스트 (owner가 아닌 클럽)
    # 기존 클럽 중 내가 owner가 아닌 것 찾기

# 동호회 가입 - 새 클럽이 아닌 기존 클럽
if existing_club_id:
    status, body = test(f"동호회 가입 POST /clubs/{existing_club_id}/join", "POST", f"/clubs/{existing_club_id}/join")
    print(f"  Join response: {str(body)[:200]}")

    if status == 200:
        # 가입됐으면 탈퇴 테스트
        status, body = test(f"동호회 탈퇴 POST /clubs/{existing_club_id}/leave", "POST", f"/clubs/{existing_club_id}/leave")
        print(f"  Leave response: {str(body)[:200]}")

print()
print("=" * 60)
print("공동구매 기능 테스트")
print("=" * 60)

# 공동구매 목록
status, body = test("공동구매 목록 GET /groupbuy", "GET", "/groupbuy")
gb_list = body.get('data', []) if isinstance(body, dict) else []
print(f"  GroupBuy count: {len(gb_list)}")

# 공동구매 등록 (target_price 사용)
gb_data = {
    "title": "테스트 공동구매 2026",
    "description": "공동구매 설명입니다. 최소 5자 이상입니다.",
    "target_price": 80000,
    "min_participants": 5,
    "max_participants": 20,
    "deadline": "2026-06-30 23:59:59",
    "category": "식품",
    "product_url": "https://example.com/product"
}
status, body = test("공동구매 등록 POST /groupbuy (target_price)", "POST", "/groupbuy", gb_data, 201)
gb_id = None
if isinstance(body, dict):
    gb_id = body.get('id') or body.get('data', {}).get('id')
    print(f"  Created gb_id: {gb_id}")

gb_existing_id = gb_list[0]['id'] if gb_list else None

if gb_existing_id:
    # 공동구매 상세
    test(f"공동구매 상세 GET /groupbuy/{gb_existing_id}", "GET", f"/groupbuy/{gb_existing_id}")

    # 참여하기
    status, body = test(f"공동구매 참여 POST /groupbuy/{gb_existing_id}/join", "POST", f"/groupbuy/{gb_existing_id}/join")
    print(f"  GB Join response: {str(body)[:200]}")

print()
print("=" * 60)
print("멘토링 기능 테스트")
print("=" * 60)

# 멘토 목록
status, body = test("멘토 목록 GET /mentors", "GET", "/mentors")
if isinstance(body, dict):
    mentor_list = body.get('data', body.get('mentors', []))
else:
    mentor_list = []
print(f"  Mentor count: {len(mentor_list)}")

# 내 멘토 프로필
test("내 멘토 프로필 GET /mentors/my", "GET", "/mentors/my")

# 멘토 등록/수정 (POST /mentors/profile)
mentor_data = {
    "field": "IT/스타트업",
    "bio": "10년 이상의 IT 스타트업 경험을 보유한 멘토입니다.",
    "years_experience": 10,
    "company": "테크스타트업",
    "position": "CTO",
    "skills": ["Python", "Leadership", "Product Management"]
}
status, body = test("멘토 프로필 등록 POST /mentors/profile", "POST", "/mentors/profile", mentor_data)
mentor_id = None
if isinstance(body, dict):
    mentor_id = body.get('id') or body.get('data', {}).get('id')
    print(f"  Created/updated mentor_id: {mentor_id}")
    print(f"  Response: {str(body)[:200]}")

# 멘토 목록에서 기존 멘토
if mentor_list:
    mentor_existing_id = mentor_list[0]['id']
    # 멘토 상세 (GET /mentors/{id})
    status, body = test(f"멘토 상세 GET /mentors/{mentor_existing_id}", "GET", f"/mentors/{mentor_existing_id}")
    print(f"  Mentor detail: {str(body)[:200]}")

    # 멘토링 신청 (자기자신 제외)
    if mentor_list[0].get('user_id') != 1:  # user_id=1이 아닌 경우만
        apply_data = {"message": "멘토링 신청합니다. 스타트업 창업에 도움이 필요합니다."}
        status, body = test(f"멘토링 신청 POST /mentors/{mentor_existing_id}/request", "POST", f"/mentors/{mentor_existing_id}/request", apply_data)
        print(f"  Apply response: {str(body)[:200]}")

# 내 멘토링 요청 목록
test("내 멘토링 요청 GET /mentors/requests", "GET", "/mentors/requests")

# available 토글
test("멘토 available 토글 POST /mentors/toggle-available", "POST", "/mentors/toggle-available")

print()
print("=" * 60)
print("테스트 결과 요약")
print("=" * 60)
passed = sum(1 for r in results if r['result'] == 'PASS')
failed = sum(1 for r in results if r['result'] == 'FAIL')
print(f"PASS: {passed}, FAIL: {failed}, TOTAL: {len(results)}")
print()
if failed > 0:
    print("실패 목록:")
    for r in results:
        if r['result'] == 'FAIL':
            print(f"  - {r['name']} (HTTP {r['status']})")
            print(f"    {r['body_preview'][:300]}")
