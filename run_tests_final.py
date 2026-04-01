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
    entry = f"[{mark}] {label} → HTTP {status} (expected {exp_str}) {notes}"
    results.append(entry)
    if not ok:
        body_str = str(body)[:250]
        results.append(f"       Body: {body_str}")
    return ok, status, body

# ============================================================
# 구인구직 (Jobs)
# ============================================================
section = "구인구직"
results.append(f"\n{'='*50}")
results.append(f"  {section}")
results.append(f"{'='*50}")

# 1. GET /api/jobs 목록, 페이지네이션
s, b = curl("GET", "/api/jobs")
ok, _, _ = check("J-1: GET /api/jobs 목록", s, b, 200)
if ok and isinstance(b, dict):
    pages = 'current_page' in b or 'meta' in b or 'links' in b
    total = b.get('total', b.get('meta', {}).get('total') if isinstance(b.get('meta'), dict) else '?')
    results.append(f"     → pagination: {pages}, total: {total}, per_page: {b.get('per_page','?')}")

# 2. 검색
s, b = curl("GET", "/api/jobs?search=manager")
check("J-2: GET /api/jobs?search=manager 검색", s, b, 200,
      f"| 결과: {len(b.get('data',[])) if isinstance(b,dict) else '?'}건")

# 3. 타입 필터
s, b = curl("GET", "/api/jobs?job_type=full_time")
check("J-3: GET /api/jobs?job_type=full_time 필터", s, b, 200)

# 4. POST /api/jobs (유저1) - job_type은 ENUM: full_time/part_time/contract/freelance
job_data = {
    "title": "Senior Manager Needed",
    "content": "Looking for experienced manager with 5+ years experience.",
    "company_name": "Test Corp",
    "job_type": "full_time",
    "region": "New York",
    "salary_range": "70000-90000",
    "contact_email": "hr@testcorp.com"
}
s, b = curl("POST", "/api/jobs", token=T1, data=job_data)
ok, _, _ = check("J-4: POST /api/jobs (유저1 작성)", s, b, [200, 201])

job_id = None
if isinstance(b, dict):
    job_id = (b.get('job', {}) or {}).get('id') or b.get('id')
    if not job_id and isinstance(b.get('data'), dict):
        job_id = b['data'].get('id')
results.append(f"     → Created job_id: {job_id}")

if not ok or not job_id:
    results.append(f"     → 신규 글 작성 실패, 기존 글 ID로 대체 시도")
    s2, b2 = curl("GET", "/api/jobs?per_page=5")
    if isinstance(b2, dict):
        items = b2.get('data', [])
        if items:
            job_id = items[0].get('id')
            u1_job = None
            for item in items:
                # find one owned by user 1
                if item.get('user_id') == 1:
                    u1_job = item.get('id')
                    break
            if u1_job:
                job_id = u1_job
    results.append(f"     → Fallback job_id: {job_id}")

# 5. PUT /api/jobs/{id} (유저1) - NOTE: PUT 라우트 없음 (설계 이슈)
results.append(f"[NOTE] J-5: jobs에는 PUT/수정 라우트 없음 (api.php 확인됨 - 설계 문제)")
results.append(f"       Route analysis: Route::delete('jobs/{{job}}') only - no PUT/update route")

# 6. PUT attempt (유저2) → 405 (route missing)
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T2, data={"title": "Hacked"})
    ok2, _, _ = check(f"J-6: PUT /api/jobs/{job_id} (유저2 타인수정) → 403/405", s, b, [403, 405])
    if s == 405:
        results.append(f"     → 405: PUT 라우트 없음 (보안적으로 무해)")

# 7. DELETE /api/jobs/{id} (유저2) → 403
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T2)
    check(f"J-7: DELETE /api/jobs/{job_id} (유저2 타인삭제) → 403", s, b, 403)

# 8. DELETE /api/jobs/{id} (유저1) → 200
if job_id:
    # First create new job to delete
    s_new, b_new = curl("POST", "/api/jobs", token=T1, data=job_data)
    del_id = None
    if isinstance(b_new, dict):
        del_id = (b_new.get('job', {}) or {}).get('id') or b_new.get('id')
    if del_id:
        s, b = curl("DELETE", f"/api/jobs/{del_id}", token=T1)
        ok, _, _ = check(f"J-8: DELETE /api/jobs/{del_id} (유저1 본인삭제)", s, b, [200, 204])
    else:
        results.append("[SKIP] J-8: 새 job 생성 실패 - 본인삭제 테스트 불가")

# 9. 좋아요, 북마크
if job_id:
    s_new, b_new = curl("POST", "/api/jobs", token=T1, data=job_data)
    like_id = None
    if isinstance(b_new, dict):
        like_id = (b_new.get('job', {}) or {}).get('id') or b_new.get('id')
    if like_id:
        s, b = curl("POST", f"/api/jobs/{like_id}/like", token=T1)
        check(f"J-9a: POST /api/jobs/{like_id}/like (좋아요 토글ON)", s, b, [200, 201])

        s, b = curl("POST", f"/api/jobs/{like_id}/like", token=T1)
        check(f"J-9b: POST /api/jobs/{like_id}/like (좋아요 토글OFF)", s, b, [200, 201])

        s, b = curl("POST", f"/api/jobs/{like_id}/bookmark", token=T1)
        check(f"J-9c: POST /api/jobs/{like_id}/bookmark (북마크)", s, b, [200, 201])

        curl("DELETE", f"/api/jobs/{like_id}", token=T1)
    else:
        results.append("[SKIP] J-9: like_id 없음")

# ============================================================
# 중고장터 (Market)
# ============================================================
section = "중고장터"
results.append(f"\n{'='*50}")
results.append(f"  {section}")
results.append(f"{'='*50}")

# 1. GET /api/market
s, b = curl("GET", "/api/market")
check("M-1: GET /api/market 목록", s, b, 200)

# 2. POST /api/market (condition ENUM: new/like_new/good/fair/poor)
market_data = {
    "title": "iPhone 14 Pro Max 256GB",
    "description": "Like new iPhone 14 Pro Max, purchased 6 months ago, no scratches",
    "price": 750,
    "category": "Electronics",
    "condition": "like_new",
    "region": "Flushing, NY"
}
s, b = curl("POST", "/api/market", token=T1, data=market_data)
ok, _, _ = check("M-2: POST /api/market (title+description+price 필수)", s, b, [200, 201])

market_id = None
if isinstance(b, dict):
    market_id = (b.get('item', {}) or {}).get('id') or b.get('id')
    if not market_id and isinstance(b.get('data'), dict):
        market_id = b['data'].get('id')
results.append(f"     → Created market_id: {market_id}")

if market_id:
    # 3a. 타인 수정 → 403
    s, b = curl("PUT", f"/api/market/{market_id}", token=T2, data={"title": "Hacked"})
    check(f"M-3a: PUT /api/market/{market_id} (유저2 타인수정) → 403", s, b, 403)

    # 3b. 타인 삭제 → 403
    s, b = curl("DELETE", f"/api/market/{market_id}", token=T2)
    check(f"M-3b: DELETE /api/market/{market_id} (유저2 타인삭제) → 403", s, b, 403)

    # 4. 거래완료 처리 (PATCH /sold 없음 → PUT status=sold)
    s, b = curl("PATCH", f"/api/market/{market_id}/sold", token=T1)
    ok, _, _ = check(f"M-4a: PATCH /api/market/{market_id}/sold", s, b, [200, 201])
    if not ok:
        results.append(f"     → PATCH /sold 라우트 없음 (api.php 확인됨)")
        s2, b2 = curl("PUT", f"/api/market/{market_id}", token=T1, data={"status": "sold"})
        ok2, _, _ = check(f"M-4b: PUT /api/market/{market_id} status=sold (대안)", s2, b2, 200)

    # 5. like, bookmark
    s, b = curl("POST", f"/api/market/{market_id}/like", token=T1)
    check(f"M-5a: POST /api/market/{market_id}/like", s, b, [200, 201])

    s, b = curl("POST", f"/api/market/{market_id}/bookmark", token=T1)
    check(f"M-5b: POST /api/market/{market_id}/bookmark", s, b, [200, 201])

    # cleanup
    curl("DELETE", f"/api/market/{market_id}", token=T1)
else:
    results.append("[SKIP] M-3,4: market_id 없음")

# ============================================================
# 부동산 (Real Estate)
# ============================================================
section = "부동산"
results.append(f"\n{'='*50}")
results.append(f"  {section}")
results.append(f"{'='*50}")

# 1. GET /api/realestate
s, b = curl("GET", "/api/realestate")
check("R-1: GET /api/realestate 목록", s, b, 200)

# 2. POST - type 한국어: 렌트|매매|룸메이트|상가|전세
#    address 필수, latitude/longitude (not lat/lng)
re_data = {
    "title": "2BR Apartment in Flushing - 렌트",
    "description": "Beautiful 2 bedroom apartment near Main St subway",
    "type": "렌트",
    "price": 2200,
    "address": "35-40 Parsons Blvd, Flushing, NY 11354",
    "region": "New York",
    "latitude": 40.7678,
    "longitude": -73.8330,
    "bedrooms": 2,
    "bathrooms": 1,
    "sqft": 900,
    "phone": "718-555-1234"
}
s, b = curl("POST", "/api/realestate", token=T1, data=re_data)
ok, _, _ = check("R-2: POST /api/realestate (type=렌트, Korean)", s, b, [200, 201])

re_id = None
if isinstance(b, dict):
    re_id = (b.get('listing', {}) or {}).get('id') or b.get('id')
    if not re_id and isinstance(b.get('data'), dict):
        re_id = b['data'].get('id')
results.append(f"     → Created realestate_id: {re_id}")

# 지도 데이터 확인 (latitude/longitude in response)
if isinstance(b, dict):
    b_str = json.dumps(b).lower()
    has_lat = '"latitude"' in b_str
    has_lng = '"longitude"' in b_str
    mark = "PASS" if (has_lat and has_lng) else "FAIL"
    results.append(f"[{mark}] R-4: 지도 데이터 latitude/longitude 포함: lat={has_lat}, lng={has_lng}")

if re_id:
    # 3a. 타인 수정 → 403
    s, b = curl("PUT", f"/api/realestate/{re_id}", token=T2, data={"title": "Hacked"})
    check(f"R-3a: PUT /api/realestate/{re_id} (유저2 타인수정) → 403", s, b, 403)

    # 3b. 타인 삭제 → 403
    s, b = curl("DELETE", f"/api/realestate/{re_id}", token=T2)
    check(f"R-3b: DELETE /api/realestate/{re_id} (유저2 타인삭제) → 403", s, b, 403)

    # bookmark
    s, b = curl("POST", f"/api/realestate/{re_id}/bookmark", token=T1)
    check(f"R-5: POST /api/realestate/{re_id}/bookmark", s, b, [200, 201])

    # cleanup
    curl("DELETE", f"/api/realestate/{re_id}", token=T1)
else:
    results.append("[SKIP] R-3,4: re_id 없음")

# ============================================================
# 이벤트 (Events)
# ============================================================
section = "이벤트"
results.append(f"\n{'='*50}")
results.append(f"  {section}")
results.append(f"{'='*50}")

# 1. GET /api/events
s, b = curl("GET", "/api/events")
check("E-1: GET /api/events 목록", s, b, 200)

# 2. POST /api/events
# category: general,meetup,food,culture,sports,education,business,social
# event_date: required, must be after:now
event_data = {
    "title": "Korean Community Meetup 2026",
    "description": "Monthly gathering for Korean Americans in NY",
    "event_date": "2026-07-15 18:00:00",
    "location": "Flushing Community Center",
    "region": "New York",
    "category": "meetup",
    "max_attendees": 50,
    "is_free": True,
    "is_online": False
}
s, b = curl("POST", "/api/events", token=T1, data=event_data)
ok, _, _ = check("E-2: POST /api/events (event_date 필수)", s, b, [200, 201])

event_id = None
if isinstance(b, dict):
    event_id = b.get('id') or (b.get('event', {}) or {}).get('id')
    if not event_id and isinstance(b.get('data'), dict):
        event_id = b['data'].get('id')
results.append(f"     → Created event_id: {event_id}")

if event_id:
    # 3. 참가신청
    s, b = curl("POST", f"/api/events/{event_id}/attend", token=T1)
    check(f"E-3: POST /api/events/{event_id}/attend (참가신청)", s, b, [200, 201])

    # 4. 좋아요
    s, b = curl("POST", f"/api/events/{event_id}/like", token=T1)
    check(f"E-4: POST /api/events/{event_id}/like (좋아요)", s, b, [200, 201])

    # 5. 북마크
    s, b = curl("POST", f"/api/events/{event_id}/bookmark", token=T1)
    check(f"E-5: POST /api/events/{event_id}/bookmark (북마크)", s, b, [200, 201])

    # 6a. 타인 수정 → 403
    s, b = curl("PUT", f"/api/events/{event_id}", token=T2, data={"title": "Hacked"})
    check(f"E-6a: PUT /api/events/{event_id} (유저2 타인수정) → 403", s, b, 403)

    # 6b. 타인 삭제 → 403 (destroy cancels, returns 200 but should protect)
    s, b = curl("DELETE", f"/api/events/{event_id}", token=T2)
    ok, _, _ = check(f"E-6b: DELETE /api/events/{event_id} (유저2 타인삭제) → 403", s, b, 403)

    # cleanup
    curl("DELETE", f"/api/events/{event_id}", token=T1)
else:
    results.append("[SKIP] E-3~6: event_id 없음")

# ============================================================
# 결과 출력
# ============================================================
print("\n" + "=" * 60)
print("최종 테스트 결과")
print("=" * 60)
passes = 0
fails = 0
skips = 0
for r in results:
    print(r)
    if r.strip().startswith("[PASS]"):
        passes += 1
    elif r.strip().startswith("[FAIL]"):
        fails += 1
    elif r.strip().startswith("[SKIP]"):
        skips += 1

print(f"\n{'='*60}")
print(f"총 PASS: {passes}  FAIL: {fails}  SKIP: {skips}")
print(f"{'='*60}")
