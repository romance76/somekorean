import json
import subprocess

BASE = "https://somekorean.com"
# User1: id=1 (Test User, non-admin)
T1 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyNzYwLCJleHAiOjE3NzQ5NjYzNjAsIm5iZiI6MTc3NDk2Mjc2MCwianRpIjoieEJoUFQwNllHbE9xVFlBWSIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.pwQUPTgynYgqgvLfw4cpf2QWykKuH5sknaGZciG1QUw"
# User2: id=53 (non-admin)
T2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyNzYwLCJleHAiOjE3NzQ5NjYzNjAsIm5iZiI6MTc3NDk2Mjc2MCwianRpIjoiV21Mb3hMWGZHdkI3eGFPVCIsInN1YiI6IjUzIiwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyJ9.tRh1lh4UwQ2lB6LV--sdwTXuoZvrtVRB80y-QQw73IA"

U1_ID = 1
U2_ID = 53

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
results.append("\n[구인구직]")

# 1. GET /api/jobs 목록, 페이지네이션
s, b = curl("GET", "/api/jobs")
ok, _, _ = check("J-1: GET /api/jobs 목록", s, b, 200)
if ok and isinstance(b, dict):
    pages = 'current_page' in b
    results.append(f"     → pagination: current_page={b.get('current_page')}, per_page={b.get('per_page')}, total={b.get('total')}, last_page={b.get('last_page')}")

# 2. 검색
s, b = curl("GET", "/api/jobs?search=manager")
cnt = len(b.get('data', [])) if isinstance(b, dict) else '?'
check(f"J-2: GET /api/jobs?search=manager 검색", s, b, 200, f"| {cnt}건 반환")

# 3. 타입 필터
s, b = curl("GET", "/api/jobs?job_type=full_time")
cnt = len(b.get('data', [])) if isinstance(b, dict) else '?'
check(f"J-3: GET /api/jobs?job_type=full_time 필터", s, b, 200, f"| {cnt}건 반환")

# 4. POST (유저1)
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
results.append(f"     → job_id: {job_id}")

# 5. PUT (유저1 본인 수정)
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T1, data={"title": "Updated Manager Position", "content": "Updated content"})
    check(f"J-5: PUT /api/jobs/{job_id} (유저1 본인수정)", s, b, 200)

# 6. PUT (유저2 타인 수정 → 403)
if job_id:
    s, b = curl("PUT", f"/api/jobs/{job_id}", token=T2, data={"title": "Hacked"})
    check(f"J-6: PUT /api/jobs/{job_id} (유저2 타인수정) → 403", s, b, 403)

# 7. DELETE (유저2 타인 삭제 → 403)
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T2)
    check(f"J-7: DELETE /api/jobs/{job_id} (유저2 타인삭제) → 403", s, b, 403)

# 8. DELETE (유저1 본인 삭제)
if job_id:
    s, b = curl("DELETE", f"/api/jobs/{job_id}", token=T1)
    check(f"J-8: DELETE /api/jobs/{job_id} (유저1 본인삭제)", s, b, [200, 204])

# 9. 좋아요, 북마크
s_new, b_new = curl("POST", "/api/jobs", token=T1, data=job_data)
like_id = (b_new.get('job', {}) or {}).get('id') if isinstance(b_new, dict) else None
if like_id:
    s, b = curl("POST", f"/api/jobs/{like_id}/like", token=T1)
    liked = b.get('liked') if isinstance(b, dict) else '?'
    check(f"J-9a: POST /api/jobs/{like_id}/like (좋아요 ON)", s, b, [200, 201], f"| liked={liked}")

    s, b = curl("POST", f"/api/jobs/{like_id}/like", token=T1)
    liked2 = b.get('liked') if isinstance(b, dict) else '?'
    check(f"J-9b: POST /api/jobs/{like_id}/like (좋아요 OFF 토글)", s, b, [200, 201], f"| liked={liked2}")

    s, b = curl("POST", f"/api/jobs/{like_id}/bookmark", token=T1)
    check(f"J-9c: POST /api/jobs/{like_id}/bookmark (북마크)", s, b, [200, 201])

    curl("DELETE", f"/api/jobs/{like_id}", token=T1)
else:
    results.append("[SKIP] J-9: like_id 없음")

# ============================================================
# 중고장터 (Market)
# ============================================================
results.append("\n[중고장터]")

s, b = curl("GET", "/api/market")
check("M-1: GET /api/market 목록", s, b, 200)

market_data = {
    "title": "iPhone 14 Pro Max 256GB",
    "description": "Like new iPhone 14 Pro Max, purchased 6 months ago, no scratches",
    "price": 750,
    "category": "Electronics",
    "condition": "like_new",
    "region": "Flushing, NY"
}
s, b = curl("POST", "/api/market", token=T1, data=market_data)
ok, _, _ = check("M-2: POST /api/market (title+description+price)", s, b, [200, 201])
market_id = (b.get('item', {}) or {}).get('id') if isinstance(b, dict) else None
results.append(f"     → market_id: {market_id}")

if market_id:
    s, b = curl("PUT", f"/api/market/{market_id}", token=T2, data={"title": "Hacked"})
    check(f"M-3a: PUT /api/market/{market_id} (유저2 타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/market/{market_id}", token=T2)
    check(f"M-3b: DELETE /api/market/{market_id} (유저2 타인삭제) → 403", s, b, 403)

    # 거래완료
    s, b = curl("PATCH", f"/api/market/{market_id}/sold", token=T1)
    ok_sold, _, _ = check(f"M-4a: PATCH /api/market/{market_id}/sold (거래완료)", s, b, [200, 201])
    if not ok_sold:
        results.append("     → PATCH /sold 없음, PUT status=sold 시도")
        s2, b2 = curl("PUT", f"/api/market/{market_id}", token=T1, data={"status": "sold"})
        check(f"M-4b: PUT /api/market/{market_id} status=sold (대안)", s2, b2, 200)

    s, b = curl("POST", f"/api/market/{market_id}/like", token=T1)
    check(f"M-5a: POST /api/market/{market_id}/like (좋아요)", s, b, [200, 201])

    s, b = curl("POST", f"/api/market/{market_id}/bookmark", token=T1)
    check(f"M-5b: POST /api/market/{market_id}/bookmark (북마크)", s, b, [200, 201])

    curl("DELETE", f"/api/market/{market_id}", token=T1)
else:
    results.append("[SKIP] M-3~5: market_id 없음")

# ============================================================
# 부동산 (Real Estate)
# ============================================================
results.append("\n[부동산]")

s, b = curl("GET", "/api/realestate")
check("R-1: GET /api/realestate 목록", s, b, 200)

re_data = {
    "title": "2BR Apartment in Flushing - Test",
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
ok, _, _ = check("R-2: POST /api/realestate (type=렌트 한국어)", s, b, [200, 201])
re_id = (b.get('listing', {}) or {}).get('id') if isinstance(b, dict) else None
results.append(f"     → realestate_id: {re_id}")

# 지도 데이터 확인
if isinstance(b, dict):
    b_str = json.dumps(b).lower()
    has_lat = '"latitude"' in b_str
    has_lng = '"longitude"' in b_str
    mark = "PASS" if (has_lat and has_lng) else "FAIL"
    results.append(f"[{mark}] R-4: 지도 데이터 latitude/longitude 포함 → lat={has_lat}, lng={has_lng}")

if re_id:
    s, b = curl("PUT", f"/api/realestate/{re_id}", token=T2, data={"title": "Hacked"})
    check(f"R-3a: PUT /api/realestate/{re_id} (유저2 타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/realestate/{re_id}", token=T2)
    check(f"R-3b: DELETE /api/realestate/{re_id} (유저2 타인삭제) → 403", s, b, 403)

    s, b = curl("POST", f"/api/realestate/{re_id}/bookmark", token=T1)
    check(f"R-5: POST /api/realestate/{re_id}/bookmark (북마크)", s, b, [200, 201])

    curl("DELETE", f"/api/realestate/{re_id}", token=T1)
else:
    results.append("[SKIP] R-3~5: re_id 없음")

# ============================================================
# 이벤트 (Events)
# ============================================================
results.append("\n[이벤트]")

s, b = curl("GET", "/api/events")
check("E-1: GET /api/events 목록", s, b, 200)

event_data = {
    "title": "Korean Community Meetup 2026",
    "description": "Monthly gathering for Korean Americans in NY",
    "event_date": "2026-08-15 18:00:00",
    "location": "Flushing Community Center, NY",
    "region": "New York",
    "category": "meetup",
    "max_attendees": 50,
    "is_free": True,
    "is_online": False
}
s, b = curl("POST", "/api/events", token=T1, data=event_data)
ok, _, _ = check("E-2: POST /api/events (event_date 필수)", s, b, [200, 201])
event_id = b.get('id') if isinstance(b, dict) else None
results.append(f"     → event_id: {event_id}")

if event_id:
    s, b = curl("POST", f"/api/events/{event_id}/attend", token=T1)
    check(f"E-3: POST /api/events/{event_id}/attend (참가신청)", s, b, [200, 201])

    s, b = curl("POST", f"/api/events/{event_id}/like", token=T1)
    check(f"E-4: POST /api/events/{event_id}/like (좋아요)", s, b, [200, 201])

    s, b = curl("POST", f"/api/events/{event_id}/bookmark", token=T1)
    check(f"E-5: POST /api/events/{event_id}/bookmark (북마크)", s, b, [200, 201])

    s, b = curl("PUT", f"/api/events/{event_id}", token=T2, data={"title": "Hacked"})
    check(f"E-6a: PUT /api/events/{event_id} (유저2 타인수정) → 403", s, b, 403)

    s, b = curl("DELETE", f"/api/events/{event_id}", token=T2)
    check(f"E-6b: DELETE /api/events/{event_id} (유저2 타인삭제) → 403", s, b, 403)

    # cleanup
    curl("DELETE", f"/api/events/{event_id}", token=T1)
else:
    results.append("[SKIP] E-3~6: event_id 없음")

# ============================================================
# 결과 출력
# ============================================================
print("\n" + "=" * 65)
print("최종 테스트 결과 (비어드민 유저 1 vs 유저 53)")
print("=" * 65)
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

print(f"\n{'='*65}")
print(f"총 PASS: {passes}  FAIL: {fails}  SKIP: {skips}")
print(f"{'='*65}")
