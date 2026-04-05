import requests
import json

BASE = "https://somekorean.com/api"

with open('/tmp/tokens.json') as f:
    t = json.load(f)

TOKEN = t['token']
TOKEN2 = t['token2']
USER2_ID = t['user2_id']

def h1():
    return {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

def h2():
    return {"Authorization": f"Bearer {TOKEN2}", "Accept": "application/json", "Content-Type": "application/json"}

results = {}

print("="*60)
print("=== MATCH API TESTS ===")
print("="*60)

# 1. 내 프로필 조회 (GET /api/match/profile)
print("\n[1] GET /api/match/profile (my profile)")
r = requests.get(f"{BASE}/match/profile", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if r.status_code == 200:
        print(f"  Profile: {json.dumps(data)[:200] if data else 'null (no profile)'}")
        results['match_my_profile'] = 'PASS'
    else:
        print(f"  Error: {json.dumps(data)[:200]}")
        results['match_my_profile'] = 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_my_profile'] = 'FAIL'

# 2. 프로필 생성/수정 (POST /api/match/profile)
print("\n[2] POST /api/match/profile (create/update profile)")
payload = {
    "nickname": "테스트유저",
    "gender": "male",
    "birth_year": 1990,
    "age_range_min": 25,
    "age_range_max": 40,
    "region": "캘리포니아",
    "bio": "안녕하세요 테스트 프로필입니다",
    "interests": ["여행", "음악", "영화"],
    "visibility": "public"
}
r = requests.post(f"{BASE}/match/profile", headers=h1(), json=payload, timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if r.status_code in [200, 201]:
        print(f"  Profile ID: {data.get('id', 'N/A')}")
        print(f"  Nickname: {data.get('nickname', 'N/A')}")
        results['match_save_profile'] = 'PASS'
    else:
        print(f"  Error: {json.dumps(data)[:300]}")
        results['match_save_profile'] = 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_save_profile'] = 'FAIL'

# Create user2 profile too
payload2 = {
    "nickname": "테스트유저2",
    "gender": "female",
    "birth_year": 1992,
    "visibility": "public"
}
r2 = requests.post(f"{BASE}/match/profile", headers=h2(), json=payload2, timeout=15)
print(f"  User2 Profile Status: {r2.status_code}")

# 3. 프로필 목록 (GET /api/match/browse)
print("\n[3] GET /api/match/browse (profiles list)")
r = requests.get(f"{BASE}/match/browse", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if r.status_code == 200:
        print(f"  Profiles count: {len(data)}")
        if data:
            print(f"  First: {data[0].get('nickname', 'N/A')} age:{data[0].get('age', 'N/A')}")
        results['match_browse'] = 'PASS'
    else:
        print(f"  Error: {json.dumps(data)[:200]}")
        results['match_browse'] = 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_browse'] = 'FAIL'

# 4. 좋아요 (POST /api/match/like/{userId})
print(f"\n[4] POST /api/match/like/{USER2_ID} (like user2)")
r = requests.post(f"{BASE}/match/like/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['match_like'] = 'PASS' if r.status_code in [200, 201] else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_like'] = 'FAIL'

# 5. 자기 자신 좋아요 시도 (400 예상)
print("\n[5] POST /api/match/like/1 (like self - should fail)")
r = requests.post(f"{BASE}/match/like/1", headers=h1(), timeout=15)
print(f"  Status: {r.status_code} (expected 400)")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['match_like_self'] = 'PASS' if r.status_code == 400 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_like_self'] = 'FAIL'

# 6. 매치 확인 (GET /api/match/matches)
print("\n[6] GET /api/match/matches")
r = requests.get(f"{BASE}/match/matches", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Matches: {len(data) if isinstance(data, list) else json.dumps(data)[:100]}")
    results['match_matches'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_matches'] = 'FAIL'

# 7. 좋아요 목록 (GET /api/match/likes)
print("\n[7] GET /api/match/likes (received likes)")
r = requests.get(f"{BASE}/match/likes", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Likes received: {len(data) if isinstance(data, list) else json.dumps(data)[:100]}")
    results['match_likes'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_likes'] = 'FAIL'

# 8. 사진 업로드 테스트 (POST /api/match/photos)
print("\n[8] POST /api/match/photos (upload photo)")
# Create a simple 1x1 pixel test image
import io
# minimal PNG bytes
png_bytes = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
    0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82
])
headers_no_ct = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
files = {'photo': ('test.png', io.BytesIO(png_bytes), 'image/png')}
r = requests.post(f"{BASE}/match/photos", headers=headers_no_ct, files=files, timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if r.status_code == 200:
        print(f"  URL: {data.get('url', 'N/A')}")
        results['match_photo_upload'] = 'PASS'
    else:
        print(f"  Error: {json.dumps(data)[:200]}")
        results['match_photo_upload'] = 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_photo_upload'] = 'FAIL'

print("\n" + "="*60)
print("=== FRIEND API TESTS ===")
print("="*60)

# 1. 친구 목록 (GET /api/friends)
print("\n[1] GET /api/friends (my friends)")
r = requests.get(f"{BASE}/friends", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Friends: {data}")
    results['friend_list'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_list'] = 'FAIL'

# 2. 친구 요청 (POST /api/friends/request/{userId})
print(f"\n[2] POST /api/friends/request/{USER2_ID} (send friend request)")
r = requests.post(f"{BASE}/friends/request/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['friend_request'] = 'PASS' if r.status_code in [200, 201, 422] else 'FAIL'
    # 422 = already exists is acceptable
    if r.status_code == 422:
        print("  (Already sent - acceptable)")
        results['friend_request'] = 'PASS'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_request'] = 'FAIL'

# 3. 대기 중인 요청 목록 (user2 입장)
print("\n[3] GET /api/friends/pending (user2's pending requests)")
r = requests.get(f"{BASE}/friends/pending", headers=h2(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Pending: {json.dumps(data)[:300]}")
    results['friend_pending'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_pending'] = 'FAIL'

# 4. 친구 수락 (user2가 user1 요청 수락)
print("\n[4] POST /api/friends/accept/1 (user2 accepts user1's request)")
r = requests.post(f"{BASE}/friends/accept/1", headers=h2(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['friend_accept'] = 'PASS' if r.status_code == 200 else 'FAIL'
    if r.status_code == 404:
        print("  (No pending request found)")
        results['friend_accept'] = 'FAIL - no pending request'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_accept'] = 'FAIL'

# 5. 친구 목록 재확인
print("\n[5] GET /api/friends (after accept)")
r = requests.get(f"{BASE}/friends", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    friends = data.get('data', [])
    print(f"  Friends count: {len(friends)}")
    results['friend_list_after'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_list_after'] = 'FAIL'

# 6. 친구 검색
print("\n[6] GET /api/friends/search?q=test")
r = requests.get(f"{BASE}/friends/search?q=test", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Results: {json.dumps(data)[:200]}")
    results['friend_search'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_search'] = 'FAIL'

# 7. 친구 삭제 (DELETE /api/friends/{userId})
print(f"\n[7] DELETE /api/friends/{USER2_ID} (remove friend)")
r = requests.delete(f"{BASE}/friends/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['friend_remove'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_remove'] = 'FAIL'

# 8. 친구 거절 테스트 (새 요청 보내고 거절)
print("\n[8] POST /api/friends/request/{USER2_ID} + reject (send then reject)")
r_req = requests.post(f"{BASE}/friends/request/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Send request status: {r_req.status_code}")
r_rej = requests.post(f"{BASE}/friends/reject/1", headers=h2(), timeout=15)
print(f"  Reject status: {r_rej.status_code}")
try:
    data = r_rej.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['friend_reject'] = 'PASS' if r_rej.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['friend_reject'] = 'FAIL'

print("\n" + "="*60)
print("=== MATCH + FRIEND TEST RESULTS ===")
print("="*60)
for k, v in results.items():
    ok = "OK" if "PASS" in str(v) else ("--" if "SKIP" in str(v) else "XX")
    print(f"  [{ok}] {k}: {v}")

with open('/tmp/match_friend_results.json', 'w') as f:
    json.dump(results, f)
