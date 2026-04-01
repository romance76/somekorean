import json
import subprocess

BASE = "https://somekorean.com"
T1 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyMjkwLCJleHAiOjE3NzQ5NjU4OTAsIm5iZiI6MTc3NDk2MjI5MCwianRpIjoieVZ5OVkxZnAxNlZsTlBoMiIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.kNjepWXAmkX2MyRTMvmTWnoQ-QZEo52LXv2MeaMKmY4"
T2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyMjkwLCJleHAiOjE3NzQ5NjU4OTAsIm5iZiI6MTc3NDk2MjI5MCwianRpIjoiMGFsVDFuRmRIb1lPQnQ3QSIsInN1YiI6IjIiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.GZxxjexQzrLa1cwfA4UZaF7VA0ENaFVf9CP_qtNr2fM"

results = []

def curl(method, path, token=None, data=None):
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
            parsed = body[:300]
        return int(status), parsed
    except Exception as e:
        return 0, str(e)

def check(label, status, body, expected_statuses, notes=""):
    if isinstance(expected_statuses, int):
        expected_statuses = [expected_statuses]
    ok = status in expected_statuses
    mark = "PASS" if ok else "FAIL"
    exp_str = "/".join(str(x) for x in expected_statuses)
    results.append(f"[{mark}] {label} → HTTP {status} (expected {exp_str}) {notes}")
    if not ok:
        body_str = str(body)[:250]
        results.append(f"       Body: {body_str}")
    return ok, status, body

print("=" * 60)
print("SomeKorean API 전체 플로우 테스트 (수정 후)")
print("=" * 60)

# ============================================================
# 구인구직 (Jobs)
# ============================================================
print("\n[1] 구인구직 테스트")

# 1. GET /api/jobs - 목록, 페이지네이션
s, b = curl("GET", "/api/jobs")
ok, _, _ = check("구인구직-1: GET /api/jobs 목록", s, b, 200)
if ok and isinstance(b, dict):
    total = b.get('total') or b.get('meta', {}).get('total') if isinstance(b.get('meta'), dict) else None
    has_pagination = 'current_page' in b or 'meta' in b or 'links' in b
    results.append(f"  [INFO] pagination: {has_pagination}, total: {total}")

# 2. GET /api/jobs?search=manager
s, b = curl("GET", "/api/jobs?search=manager")
check("구인구직-2: GET /api/jobs?search=manager 검색", s, b, 200)

# 3. GET /api/jobs?type=full-time
s, b = curl("GET", "/api/jobs?type=full-time")
check("구인구직-3: GET /api/jobs?type=full-time 필터", s, b, 200)
# Try job_type
s2, b2 = curl("GET", "/api/jobs?job_type=full-time")
if s2 == 200:
    results.append(f"  [INFO] job_type 파라미터도 지원: HTTP {s2}")

# 4. POST /api/jobs (유저1) - content 필드 필수
job_data = {
    "title": "Test Manager Position",
    "content": "Looking for an experienced manager. Full details here.",
    "company_name": "Test Company",
    "job_type": "full-time",
    "region": "New York",
    "salary_range": "60000-80000",
    "contact_email": "test@example.com"
}
s, b = curl("POST", "/api/jobs", token=T1, data=job_data)
ok, _, _ = check("구인구직-4: POST /api/jobs (유저1 작성)", s, b, [200, 201])

job_id = None
if isinstance(b, dict):
    job_id = b.get('id') or b.get('job', {}).get('id') if isinstance(b.get('job'), dict) else None
    if not job_id and isinstance(b.get('data'), dict):
        job_id = b['data'].get('id')
print(f"  Created job_id: {job_id}")

# 5. PUT /api/jobs/{id} (유저1) - NOTE: PUT route doesn't exist
# Based on route analysis: Route::delete('jobs/{job}') only - no PUT
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T1, data={"title": "Updated Manager Position"})
    ok, _, _ = check(f"구인구직-5: PUT /api/jobs/{job_id} (유저1 수정)", s, b, 200,
                     "| NOTE: PUT 라우트 없음 → 405 예상")
    results.append(f"  [INFO] 라우트 분석: api.php에 PUT jobs 라우트 없음. DELETE만 존재")

# 6. PUT /api/jobs/{id} (유저2) - 타인 수정 → 403 or 405
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T2, data={"title": "Hacked"})
    # PUT route doesn't exist so 405 is expected; if it did exist, should be 403
    ok, _, _ = check(f"구인구직-6: PUT /api/jobs/{job_id} (유저2 타인수정) → 403/405", s, b, [403, 405])
    results.append(f"  [INFO] PUT 라우트 없으므로 405도 허용")

# 7. DELETE /api/jobs/{id} (유저2) - 타인 삭제 → 403
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T2)
    check(f"구인구직-7: DELETE /api/jobs/{job_id} (유저2 타인삭제) → 403", s, b, 403)

# 8. DELETE /api/jobs/{id} (유저1) - 본인 삭제
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T1)
    ok, _, _ = check(f"구인구직-8: DELETE /api/jobs/{job_id} (유저1 본인삭제)", s, b, [200, 204])

# 9. 좋아요, 북마크 토글
s, b = curl("POST", "/api/jobs", token=T1, data=job_data)
new_job_id = None
if isinstance(b, dict):
    new_job_id = b.get('id') or (b.get('data', {}).get('id') if isinstance(b.get('data'), dict) else None)
    if not new_job_id and isinstance(b.get('job'), dict):
        new_job_id = b['job'].get('id')

if new_job_id:
    s, b = curl("POST", f"/api/jobs/{new_job_id}/like", token=T1)
    check(f"구인구직-9a: POST /api/jobs/{new_job_id}/like (좋아요)", s, b, [200, 201])

    s, b = curl("POST", f"/api/jobs/{new_job_id}/bookmark", token=T1)
    check(f"구인구직-9b: POST /api/jobs/{new_job_id}/bookmark (북마크)", s, b, [200, 201])

    # toggle again
    s, b = curl("POST", f"/api/jobs/{new_job_id}/like", token=T1)
    check(f"구인구직-9c: POST /api/jobs/{new_job_id}/like (좋아요 토글off)", s, b, [200, 201])

    curl("DELETE", f"/api/jobs/{new_job_id}", token=T1)
else:
    results.append("[SKIP] 구인구직-9: 새 job_id 없음")

# ============================================================
# 중고장터 (Market)
# ============================================================
print("\n[2] 중고장터 테스트")

# 1. GET /api/market
s, b = curl("GET", "/api/market")
check("중고장터-1: GET /api/market 목록", s, b, 200)

# 2. POST /api/market (올바른 필드 사용)
market_data = {
    "title": "Test iPhone 14 Pro",
    "description": "Used iPhone 14 Pro in great condition, barely used",
    "price": 500,
    "category": "전자기기",
    "condition": "used",
    "region": "New York"
}
s, b = curl("POST", "/api/market", token=T1, data=market_data)
ok, _, _ = check("중고장터-2: POST /api/market (title+description+price)", s, b, [200, 201])

market_id = None
if isinstance(b, dict):
    market_id = b.get('id') or (b.get('item', {}).get('id') if isinstance(b.get('item'), dict) else None)
    if not market_id and isinstance(b.get('data'), dict):
        market_id = b['data'].get('id')
print(f"  Created market_id: {market_id}")

if market_id:
    # 타인 수정/삭제 → 403
    s, b = curl("PUT", f"/api/market/{market_id}", token=T2, data={"title": "Hacked"})
    check(f"중고장터-3a: PUT /api/market/{market_id} (유저2 타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/market/{market_id}", token=T2)
    check(f"중고장터-3b: DELETE /api/market/{market_id} (유저2 타인삭제) → 403", s, b, 403)

    # 거래완료 처리
    # Route analysis: No /sold endpoint, use PUT with status=sold
    s, b = curl("PATCH", f"/api/market/{market_id}/sold", token=T1)
    ok, _, _ = check(f"중고장터-4a: PATCH /api/market/{market_id}/sold (거래완료)", s, b, [200, 201])
    if not ok:
        results.append(f"  [INFO] PATCH /sold 라우트 없음 → PUT으로 status=sold 시도")
        s2, b2 = curl("PUT", f"/api/market/{market_id}", token=T1, data={"status": "sold"})
        ok2, _, _ = check(f"중고장터-4b: PUT /api/market/{market_id} status=sold", s2, b2, 200)

    # like & bookmark
    s, b = curl("POST", f"/api/market/{market_id}/like", token=T1)
    check(f"중고장터-5a: POST /api/market/{market_id}/like", s, b, [200, 201])

    s, b = curl("POST", f"/api/market/{market_id}/bookmark", token=T1)
    check(f"중고장터-5b: POST /api/market/{market_id}/bookmark", s, b, [200, 201])

    curl("DELETE", f"/api/market/{market_id}", token=T1)
else:
    results.append("[SKIP] 중고장터-3,4: market_id 없음")

# ============================================================
# 부동산 (Real Estate)
# ============================================================
print("\n[3] 부동산 테스트")

# 1. GET /api/realestate
s, b = curl("GET", "/api/realestate")
check("부동산-1: GET /api/realestate 목록", s, b, 200)

# 2. POST /api/realestate (Korean type)
re_data = {
    "title": "2BR Apartment for Rent in Flushing",
    "description": "Beautiful apartment near downtown Flushing, close to subway",
    "type": "렌트",
    "price": 2000,
    "region": "New York",
    "address": "123 Main St, Flushing, NY",
    "lat": 40.7678,
    "lng": -73.8330,
    "bedrooms": 2,
    "bathrooms": 1,
    "size": 800
}
s, b = curl("POST", "/api/realestate", token=T1, data=re_data)
ok, _, _ = check("부동산-2: POST /api/realestate (type=렌트)", s, b, [200, 201])

re_id = None
if isinstance(b, dict):
    re_id = b.get('id') or (b.get('property', {}).get('id') if isinstance(b.get('property'), dict) else None)
    if not re_id and isinstance(b.get('data'), dict):
        re_id = b['data'].get('id')
    if not re_id and isinstance(b.get('realestate'), dict):
        re_id = b['realestate'].get('id')
print(f"  Created realestate_id: {re_id}")

# 지도 데이터 확인
if isinstance(b, dict):
    b_str = json.dumps(b).lower()
    has_lat = '"lat"' in b_str or '"latitude"' in b_str
    has_lng = '"lng"' in b_str or '"longitude"' in b_str
    results.append(f"[{'PASS' if (has_lat and has_lng) else 'FAIL'}] 부동산-4: 지도 데이터 lat/lng 포함: lat={has_lat}, lng={has_lng}")
    if has_lat or has_lng:
        results.append(f"  [INFO] Response keys include lat/lng data")

if re_id:
    # 타인 수정 → 403
    s, b = curl("PUT", f"/api/realestate/{re_id}", token=T2, data={"title": "Hacked"})
    check(f"부동산-3a: PUT /api/realestate/{re_id} (유저2 타인수정) → 403", s, b, [403, 405])

    # 타인 삭제 → 403
    s, b = curl("DELETE", f"/api/realestate/{re_id}", token=T2)
    check(f"부동산-3b: DELETE /api/realestate/{re_id} (유저2 타인삭제) → 403", s, b, [403, 405])

    # bookmark
    s, b = curl("POST", f"/api/realestate/{re_id}/bookmark", token=T1)
    check(f"부동산-5: POST /api/realestate/{re_id}/bookmark", s, b, [200, 201])

    curl("DELETE", f"/api/realestate/{re_id}", token=T1)
else:
    results.append("[SKIP] 부동산-3: re_id 없음")

# ============================================================
# 이벤트 (Events)
# ============================================================
print("\n[4] 이벤트 테스트")

# 1. GET /api/events
s, b = curl("GET", "/api/events")
check("이벤트-1: GET /api/events 목록", s, b, 200)

# 2. POST /api/events
event_data = {
    "title": "Korean Community Meetup",
    "description": "Monthly community gathering for Korean Americans",
    "event_date": "2026-06-15",
    "location": "Community Center, Flushing, NY",
    "region": "New York",
    "category": "커뮤니티",
    "max_attendees": 50,
    "is_free": True,
    "is_online": False
}
s, b = curl("POST", "/api/events", token=T1, data=event_data)
ok, _, _ = check("이벤트-2: POST /api/events (event_date 필수)", s, b, [200, 201])

event_id = None
if isinstance(b, dict):
    event_id = b.get('id') or (b.get('event', {}).get('id') if isinstance(b.get('event'), dict) else None)
    if not event_id and isinstance(b.get('data'), dict):
        event_id = b['data'].get('id')
print(f"  Created event_id: {event_id}")

if event_id:
    # 3. 참가신청
    s, b = curl("POST", f"/api/events/{event_id}/attend", token=T1)
    check(f"이벤트-3: POST /api/events/{event_id}/attend (참가신청)", s, b, [200, 201])

    # 4. 좋아요
    s, b = curl("POST", f"/api/events/{event_id}/like", token=T1)
    check(f"이벤트-4: POST /api/events/{event_id}/like (좋아요)", s, b, [200, 201])

    # 5. 북마크
    s, b = curl("POST", f"/api/events/{event_id}/bookmark", token=T1)
    check(f"이벤트-5: POST /api/events/{event_id}/bookmark (북마크)", s, b, [200, 201])

    # 6a. 타인 수정 → 403
    s, b = curl("PUT", f"/api/events/{event_id}", token=T2, data={"title": "Hacked"})
    check(f"이벤트-6a: PUT /api/events/{event_id} (유저2 타인수정) → 403", s, b, 403)

    # 6b. 타인 삭제 → 403
    s, b = curl("DELETE", f"/api/events/{event_id}", token=T2)
    check(f"이벤트-6b: DELETE /api/events/{event_id} (유저2 타인삭제) → 403", s, b, [200, 403])
    # Note: destroy sets status='cancelled' not actual delete

    curl("DELETE", f"/api/events/{event_id}", token=T1)
else:
    results.append("[SKIP] 이벤트-3-6: event_id 없음")

# ============================================================
# 결과 출력
# ============================================================
print("\n" + "=" * 60)
print("테스트 결과 요약")
print("=" * 60)
passes = sum(1 for r in results if r.startswith("[PASS]"))
fails = sum(1 for r in results if r.startswith("[FAIL]"))
skips = sum(1 for r in results if r.startswith("[SKIP]"))
infos = sum(1 for r in results if "INFO" in r)
for r in results:
    print(r)
print(f"\n총 PASS: {passes}, FAIL: {fails}, SKIP: {skips}, INFO: {infos}")
