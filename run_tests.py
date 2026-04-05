import paramiko
import json
import subprocess
import sys

BASE = "https://somekorean.com"
U1_ID = "1"
U2_ID = "2"
T1 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyMjkwLCJleHAiOjE3NzQ5NjU4OTAsIm5iZiI6MTc3NDk2MjI5MCwianRpIjoieVZ5OVkxZnAxNlZsTlBoMiIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.kNjepWXAmkX2MyRTMvmTWnoQ-QZEo52LXv2MeaMKmY4"
T2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyMjkwLCJleHAiOjE3NzQ5NjU4OTAsIm5iZiI6MTc3NDk2MjI5MCwianRpIjoiMGFsVDFuRmRIb1lPQnQ3QSIsInN1YiI6IjIiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.GZxxjexQzrLa1cwfA4UZaF7VA0ENaFVf9CP_qtNr2fM"

results = []

def curl(method, path, token=None, data=None, label=""):
    cmd = ["curl", "-s", "-w", "\n__STATUS__%{http_code}", "-X", method]
    cmd += [f"{BASE}{path}"]
    cmd += ["-H", "Accept: application/json", "-H", "Content-Type: application/json"]
    if token:
        cmd += ["-H", f"Authorization: Bearer {token}"]
    if data:
        cmd += ["-d", json.dumps(data)]
    try:
        out = subprocess.check_output(cmd, timeout=30).decode(errors='replace')
        parts = out.rsplit("__STATUS__", 1)
        body = parts[0].strip()
        status = parts[1].strip() if len(parts) > 1 else "000"
        try:
            parsed = json.loads(body)
        except:
            parsed = body[:200]
        return int(status), parsed
    except Exception as e:
        return 0, str(e)

def check(label, status, body, expected_status, notes=""):
    ok = status == expected_status
    mark = "PASS" if ok else "FAIL"
    results.append(f"[{mark}] {label} → HTTP {status} (expected {expected_status}) {notes}")
    if not ok:
        results.append(f"       Body: {str(body)[:200]}")
    return ok, status, body

print("=" * 60)
print("SomeKorean API 전체 플로우 테스트")
print("=" * 60)

# ============================================================
# 구인구직 (Jobs)
# ============================================================
print("\n[1] 구인구직 테스트")

# 1. GET /api/jobs - 목록
s, b = curl("GET", "/api/jobs", label="jobs list")
check("구인구직 1: GET /api/jobs 목록", s, b, 200,
      f"| data count: {len(b.get('data', b.get('jobs', []))) if isinstance(b, dict) else '?'}")

# 2. GET /api/jobs?search=manager
s, b = curl("GET", "/api/jobs?search=manager")
check("구인구직 2: GET /api/jobs?search=manager", s, b, 200)

# 3. GET /api/jobs?type=full-time
s, b = curl("GET", "/api/jobs?type=full-time")
check("구인구직 3: GET /api/jobs?type=full-time 필터", s, b, 200)

# 4. POST /api/jobs (유저1) - 작성
job_data = {
    "title": "Test Manager Position",
    "company": "Test Company",
    "description": "Looking for an experienced manager",
    "type": "full-time",
    "location": "New York",
    "salary": "60000-80000",
    "contact_email": "test@example.com"
}
s, b = curl("POST", "/api/jobs", token=T1, data=job_data)
ok, _, _ = check("구인구직 4: POST /api/jobs (유저1 작성)", s, b, 201)
if not ok and s == 200:
    results[-1] = results[-1].replace("FAIL", "PASS").replace("(expected 201)", "(expected 201, got 200 - OK)")
    ok = True

# Extract job ID
job_id = None
if isinstance(b, dict):
    job_id = b.get('id') or b.get('job', {}).get('id') if isinstance(b.get('job'), dict) else None
    if not job_id and 'data' in b and isinstance(b['data'], dict):
        job_id = b['data'].get('id')
print(f"  Created job_id: {job_id}")

if not job_id:
    # Get from list
    s2, b2 = curl("GET", "/api/jobs?per_page=1")
    if isinstance(b2, dict):
        items = b2.get('data', b2.get('jobs', []))
        if items and len(items) > 0:
            job_id = items[0].get('id') if isinstance(items[0], dict) else None

# 5. PUT /api/jobs/{id} (유저1) - 본인 수정
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T1, data={"title": "Updated Manager Position"})
    ok, _, _ = check(f"구인구직 5: PUT /api/jobs/{job_id} (유저1 수정)", s, b, 200)
else:
    results.append("[SKIP] 구인구직 5: job_id 없음")

# 6. PUT /api/jobs/{id} (유저2) - 타인 수정 → 403
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T2, data={"title": "Hacked"})
    check(f"구인구직 6: PUT /api/jobs/{job_id} (유저2 타인수정) → 403", s, b, 403)
else:
    results.append("[SKIP] 구인구직 6: job_id 없음")

# 7. DELETE /api/jobs/{id} (유저2) - 타인 삭제 → 403
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T2)
    check(f"구인구직 7: DELETE /api/jobs/{job_id} (유저2 타인삭제) → 403", s, b, 403)
else:
    results.append("[SKIP] 구인구직 7: job_id 없음")

# 8. DELETE /api/jobs/{id} (유저1) - 본인 삭제
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T1)
    ok, _, _ = check(f"구인구직 8: DELETE /api/jobs/{job_id} (유저1 삭제)", s, b, 200)
    if not ok and s == 204:
        results[-1] = results[-1].replace("FAIL", "PASS").replace("(expected 200)", "(expected 200, got 204 - OK)")
else:
    results.append("[SKIP] 구인구직 8: job_id 없음")

# 9. 좋아요, 북마크 테스트 - 새 글 작성 후 테스트
s, b = curl("POST", "/api/jobs", token=T1, data=job_data)
new_job_id = None
if isinstance(b, dict):
    new_job_id = b.get('id') or (b.get('data', {}).get('id') if isinstance(b.get('data'), dict) else None)
    if not new_job_id and isinstance(b.get('job'), dict):
        new_job_id = b['job'].get('id')

if new_job_id:
    s, b = curl("POST", f"/api/jobs/{new_job_id}/like", token=T1)
    ok, _, _ = check(f"구인구직 9a: POST /api/jobs/{new_job_id}/like (좋아요)", s, b, 200)
    if not ok and s == 201:
        results[-1] = results[-1].replace("FAIL", "PASS")

    s, b = curl("POST", f"/api/jobs/{new_job_id}/bookmark", token=T1)
    ok, _, _ = check(f"구인구직 9b: POST /api/jobs/{new_job_id}/bookmark (북마크)", s, b, 200)
    if not ok and s == 201:
        results[-1] = results[-1].replace("FAIL", "PASS")
    # cleanup
    curl("DELETE", f"/api/jobs/{new_job_id}", token=T1)
else:
    results.append("[SKIP] 구인구직 9: 새 job_id 없음")

# ============================================================
# 중고장터 (Market)
# ============================================================
print("\n[2] 중고장터 테스트")

# 1. GET /api/market
s, b = curl("GET", "/api/market")
check("중고장터 1: GET /api/market 목록", s, b, 200)

# 2. POST /api/market
market_data = {
    "title": "Test iPhone 14",
    "description": "Used iPhone 14 in great condition",
    "price": 500,
    "category": "전자기기",
    "condition": "used",
    "location": "New York"
}
s, b = curl("POST", "/api/market", token=T1, data=market_data)
ok, _, _ = check("중고장터 2: POST /api/market (상품등록)", s, b, 201)
if not ok and s == 200:
    results[-1] = results[-1].replace("FAIL", "PASS")

market_id = None
if isinstance(b, dict):
    market_id = b.get('id') or (b.get('data', {}).get('id') if isinstance(b.get('data'), dict) else None)
    if not market_id and isinstance(b.get('item'), dict):
        market_id = b['item'].get('id')
print(f"  Created market_id: {market_id}")

# 타인 수정/삭제 시도
if market_id:
    s, b = curl("PUT", f"/api/market/{market_id}", token=T2, data={"title": "Hacked"})
    check(f"중고장터 3a: PUT /api/market/{market_id} (타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/market/{market_id}", token=T2)
    check(f"중고장터 3b: DELETE /api/market/{market_id} (타인삭제) → 403", s, b, 403)

    # 거래완료 처리
    s, b = curl("PATCH", f"/api/market/{market_id}/sold", token=T1)
    ok, _, _ = check(f"중고장터 4: PATCH /api/market/{market_id}/sold (거래완료)", s, b, 200)
    if not ok:
        results[-1] += f" | alt: try PUT"
        s2, b2 = curl("PUT", f"/api/market/{market_id}", token=T1, data={"status": "sold"})
        if s2 == 200:
            results.append(f"  [INFO] PUT /api/market/{market_id} with status=sold → {s2}")

    # cleanup
    curl("DELETE", f"/api/market/{market_id}", token=T1)
else:
    results.append("[SKIP] 중고장터 3,4: market_id 없음")

# ============================================================
# 부동산 (Real Estate)
# ============================================================
print("\n[3] 부동산 테스트")

# 1. GET /api/realestate
s, b = curl("GET", "/api/realestate")
check("부동산 1: GET /api/realestate 목록", s, b, 200)

# 2. POST /api/realestate (Korean type)
re_data = {
    "title": "Test Apartment for Rent",
    "description": "Beautiful apartment near downtown",
    "type": "렌트",
    "price": 2000,
    "location": "New York, NY",
    "address": "123 Main St, New York, NY",
    "lat": 40.7128,
    "lng": -74.0060,
    "bedrooms": 2,
    "bathrooms": 1,
    "area": 800
}
s, b = curl("POST", "/api/realestate", token=T1, data=re_data)
ok, _, _ = check("부동산 2: POST /api/realestate (type=렌트)", s, b, 201)
if not ok and s == 200:
    results[-1] = results[-1].replace("FAIL", "PASS")

re_id = None
if isinstance(b, dict):
    re_id = b.get('id') or (b.get('data', {}).get('id') if isinstance(b.get('data'), dict) else None)
    if not re_id and isinstance(b.get('realestate'), dict):
        re_id = b['realestate'].get('id')
    if not re_id and isinstance(b.get('property'), dict):
        re_id = b['property'].get('id')
print(f"  Created realestate_id: {re_id}")

# Check lat/lng in response
if isinstance(b, dict):
    data_obj = b.get('data', b)
    has_lat = 'lat' in str(b) or 'latitude' in str(b)
    results.append(f"[{'PASS' if has_lat else 'FAIL'}] 부동산 4: 지도 데이터 (lat/lng) 포함 확인: {has_lat}")

if re_id:
    s, b = curl("PUT", f"/api/realestate/{re_id}", token=T2, data={"title": "Hacked"})
    check(f"부동산 3a: PUT /api/realestate/{re_id} (타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/realestate/{re_id}", token=T2)
    check(f"부동산 3b: DELETE /api/realestate/{re_id} (타인삭제) → 403", s, b, 403)

    # cleanup
    curl("DELETE", f"/api/realestate/{re_id}", token=T1)
else:
    results.append("[SKIP] 부동산 3: re_id 없음")

# ============================================================
# 이벤트 (Events)
# ============================================================
print("\n[4] 이벤트 테스트")

# 1. GET /api/events
s, b = curl("GET", "/api/events")
check("이벤트 1: GET /api/events 목록", s, b, 200)

# 2. POST /api/events
event_data = {
    "title": "Korean Community Meetup",
    "description": "Monthly community gathering",
    "event_date": "2026-06-15",
    "start_time": "18:00",
    "end_time": "21:00",
    "location": "Community Center, New York",
    "category": "커뮤니티",
    "max_attendees": 50,
    "is_free": True
}
s, b = curl("POST", "/api/events", token=T1, data=event_data)
ok, _, _ = check("이벤트 2: POST /api/events (event_date 필수)", s, b, 201)
if not ok and s == 200:
    results[-1] = results[-1].replace("FAIL", "PASS")

event_id = None
if isinstance(b, dict):
    event_id = b.get('id') or (b.get('data', {}).get('id') if isinstance(b.get('data'), dict) else None)
    if not event_id and isinstance(b.get('event'), dict):
        event_id = b['event'].get('id')
print(f"  Created event_id: {event_id}")

if event_id:
    # 3. 참가신청
    s, b = curl("POST", f"/api/events/{event_id}/attend", token=T1)
    ok, _, _ = check(f"이벤트 3: POST /api/events/{event_id}/attend (참가신청)", s, b, 200)
    if not ok and s == 201:
        results[-1] = results[-1].replace("FAIL", "PASS")

    # 4. 좋아요
    s, b = curl("POST", f"/api/events/{event_id}/like", token=T1)
    ok, _, _ = check(f"이벤트 4: POST /api/events/{event_id}/like (좋아요)", s, b, 200)
    if not ok and s == 201:
        results[-1] = results[-1].replace("FAIL", "PASS")

    # 5. 북마크
    s, b = curl("POST", f"/api/events/{event_id}/bookmark", token=T1)
    ok, _, _ = check(f"이벤트 5: POST /api/events/{event_id}/bookmark (북마크)", s, b, 200)
    if not ok and s == 201:
        results[-1] = results[-1].replace("FAIL", "PASS")

    # 6. 타인 수정/삭제
    s, b = curl("PUT", f"/api/events/{event_id}", token=T2, data={"title": "Hacked"})
    check(f"이벤트 6a: PUT /api/events/{event_id} (타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/events/{event_id}", token=T2)
    check(f"이벤트 6b: DELETE /api/events/{event_id} (타인삭제) → 403", s, b, 403)

    # cleanup
    curl("DELETE", f"/api/events/{event_id}", token=T1)
else:
    results.append("[SKIP] 이벤트 3-6: event_id 없음")

# ============================================================
# 결과 출력
# ============================================================
print("\n" + "=" * 60)
print("테스트 결과 요약")
print("=" * 60)
passes = sum(1 for r in results if r.startswith("[PASS]"))
fails = sum(1 for r in results if r.startswith("[FAIL]"))
skips = sum(1 for r in results if r.startswith("[SKIP]"))
for r in results:
    print(r)
print(f"\n총 PASS: {passes}, FAIL: {fails}, SKIP: {skips}")
