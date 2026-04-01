import requests
import json
import sys

BASE_URL = "https://somekorean.com/api"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTMwNzYzLCJleHAiOjE3NzQ5MzQzNjMsIm5iZiI6MTc3NDkzMDc2MywianRpIjoicXJ4RzRRTThzaWNsdXBlRSIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.0iky1XGbdmWSCPAAv7biWPuuH6BQbbr_MB5QS4olIaY"

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

        passed = status == expected_status or (expected_status == 200 and status in [200, 201])
        result = "PASS" if passed else "FAIL"
        results.append({
            "name": name,
            "result": result,
            "status": status,
            "body_preview": str(body)[:200]
        })
        print(f"[{result}] {name} - HTTP {status}")
        if not passed:
            print(f"  Response: {str(body)[:300]}")
        return status, body
    except Exception as e:
        results.append({"name": name, "result": "FAIL", "status": "ERROR", "body_preview": str(e)})
        print(f"[FAIL] {name} - ERROR: {e}")
        return None, None

print("=" * 60)
print("이벤트 기능 테스트")
print("=" * 60)

# 1. 이벤트 목록
status, body = test("이벤트 목록 GET /events", "GET", "/events")
print(f"  Events count: {len(body.get('data', body.get('events', []))) if isinstance(body, dict) else 'N/A'}")

# 날짜 필터
test("이벤트 날짜 필터", "GET", "/events?start_date=2024-01-01&end_date=2026-12-31")

# 카테고리 필터
test("이벤트 카테고리 필터", "GET", "/events?category=문화")

# 검색
test("이벤트 검색", "GET", "/events?search=한인")

# 2. 이벤트 등록
event_data = {
    "title": "테스트 이벤트",
    "description": "테스트 설명입니다",
    "event_date": "2026-04-15",
    "event_time": "14:00",
    "location": "뉴욕 한인회관",
    "category": "문화",
    "max_participants": 50,
    "price": 0
}
status, body = test("이벤트 등록 POST /events", "POST", "/events", event_data, 201)
event_id = None
if isinstance(body, dict):
    event_id = body.get('data', {}).get('id') or body.get('id') or body.get('event', {}).get('id')
    print(f"  Created event_id: {event_id}")

# event_date 없이 등록 (에러 예상)
event_data_no_date = {
    "title": "날짜없는 이벤트",
    "description": "테스트",
    "location": "뉴욕"
}
test("이벤트 등록 (event_date 없음) - 422 예상", "POST", "/events", event_data_no_date, 422)

if event_id:
    # 3. 이벤트 상세
    test(f"이벤트 상세 GET /events/{event_id}", "GET", f"/events/{event_id}")

    # 4. 이벤트 수정
    test(f"이벤트 수정 PUT /events/{event_id}", "PUT", f"/events/{event_id}", {
        "title": "수정된 테스트 이벤트",
        "event_date": "2026-04-20"
    })

    # 5. 이벤트 참가신청
    status, body = test(f"이벤트 참가신청 POST /events/{event_id}/attend", "POST", f"/events/{event_id}/attend")
    print(f"  Attend response: {str(body)[:200]}")

    # 6. 북마크
    status, body = test(f"이벤트 북마크 POST /events/{event_id}/bookmark", "POST", f"/events/{event_id}/bookmark")
    print(f"  Bookmark response: {str(body)[:200]}")

    # 좋아요
    status, body = test(f"이벤트 좋아요 POST /events/{event_id}/like", "POST", f"/events/{event_id}/like")
    print(f"  Like response: {str(body)[:200]}")

    # 7. 이벤트 삭제
    test(f"이벤트 삭제 DELETE /events/{event_id}", "DELETE", f"/events/{event_id}")

print()
print("=" * 60)
print("동호회 기능 테스트")
print("=" * 60)

# 동호회 목록
status, body = test("동호회 목록 GET /clubs", "GET", "/clubs")
print(f"  Clubs count: {len(body.get('data', body.get('clubs', []))) if isinstance(body, dict) else 'N/A'}")

# 동호회 생성
club_data = {
    "name": "테스트 동호회",
    "description": "테스트 동호회입니다",
    "category": "스포츠",
    "location": "뉴욕",
    "max_members": 30
}
status, body = test("동호회 생성 POST /clubs", "POST", "/clubs", club_data, 201)
club_id = None
if isinstance(body, dict):
    club_id = body.get('data', {}).get('id') or body.get('id') or body.get('club', {}).get('id')
    print(f"  Created club_id: {club_id}")

if club_id:
    # 동호회 상세
    test(f"동호회 상세 GET /clubs/{club_id}", "GET", f"/clubs/{club_id}")

    # 동호회 가입
    status, body = test(f"동호회 가입 POST /clubs/{club_id}/join", "POST", f"/clubs/{club_id}/join")
    print(f"  Join response: {str(body)[:200]}")

    # 동호회 게시판
    test(f"동호회 게시판 GET /clubs/{club_id}/posts", "GET", f"/clubs/{club_id}/posts")

    # 게시판 글쓰기
    post_data = {"title": "테스트 글", "content": "테스트 내용입니다"}
    status, body = test(f"동호회 게시글 등록 POST /clubs/{club_id}/posts", "POST", f"/clubs/{club_id}/posts", post_data, 201)
    print(f"  Post response: {str(body)[:200]}")

    # 동호회 탈퇴
    status, body = test(f"동호회 탈퇴 POST /clubs/{club_id}/leave", "POST", f"/clubs/{club_id}/leave")
    print(f"  Leave response: {str(body)[:200]}")

print()
print("=" * 60)
print("공동구매 기능 테스트")
print("=" * 60)

# 공동구매 목록
status, body = test("공동구매 목록 GET /groupbuy", "GET", "/groupbuy")
print(f"  GroupBuy count: {len(body.get('data', body.get('groupbuys', []))) if isinstance(body, dict) else 'N/A'}")

# 공동구매 등록
gb_data = {
    "title": "테스트 공동구매",
    "description": "공동구매 설명",
    "product_name": "테스트 상품",
    "original_price": 100000,
    "discount_price": 80000,
    "min_participants": 5,
    "max_participants": 20,
    "deadline": "2026-04-30",
    "category": "식품"
}
status, body = test("공동구매 등록 POST /groupbuy", "POST", "/groupbuy", gb_data, 201)
gb_id = None
if isinstance(body, dict):
    gb_id = body.get('data', {}).get('id') or body.get('id') or body.get('groupbuy', {}).get('id')
    print(f"  Created gb_id: {gb_id}")

if gb_id:
    # 공동구매 상세
    test(f"공동구매 상세 GET /groupbuy/{gb_id}", "GET", f"/groupbuy/{gb_id}")

    # 참여하기
    status, body = test(f"공동구매 참여 POST /groupbuy/{gb_id}/join", "POST", f"/groupbuy/{gb_id}/join")
    print(f"  GB Join response: {str(body)[:200]}")

print()
print("=" * 60)
print("멘토링 기능 테스트")
print("=" * 60)

# 멘토 목록
status, body = test("멘토 목록 GET /mentor", "GET", "/mentor")
print(f"  Mentor count: {len(body.get('data', body.get('mentors', []))) if isinstance(body, dict) else 'N/A'}")

# 멘토 등록
mentor_data = {
    "title": "스타트업 멘토링",
    "description": "IT 스타트업 관련 멘토링",
    "expertise": "IT, 스타트업",
    "experience_years": 10,
    "price_per_hour": 100,
    "available": True,
    "category": "비즈니스"
}
status, body = test("멘토 등록 POST /mentor", "POST", "/mentor", mentor_data, 201)
mentor_id = None
if isinstance(body, dict):
    mentor_id = body.get('data', {}).get('id') or body.get('id') or body.get('mentor', {}).get('id')
    print(f"  Created mentor_id: {mentor_id}")

if mentor_id:
    # 멘토 상세
    test(f"멘토 상세 GET /mentor/{mentor_id}", "GET", f"/mentor/{mentor_id}")

    # 멘토링 신청
    apply_data = {
        "message": "멘토링 신청합니다",
        "preferred_date": "2026-04-15",
        "preferred_time": "14:00"
    }
    status, body = test(f"멘토링 신청 POST /mentor/{mentor_id}/apply", "POST", f"/mentor/{mentor_id}/apply", apply_data)
    print(f"  Apply response: {str(body)[:200]}")

print()
print("=" * 60)
print("테스트 결과 요약")
print("=" * 60)
passed = sum(1 for r in results if r['result'] == 'PASS')
failed = sum(1 for r in results if r['result'] == 'FAIL')
print(f"PASS: {passed}, FAIL: {failed}, TOTAL: {len(results)}")
print()
print("실패 목록:")
for r in results:
    if r['result'] == 'FAIL':
        print(f"  - {r['name']} (HTTP {r['status']})")
        print(f"    {r['body_preview'][:200]}")
