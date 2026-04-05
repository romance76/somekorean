import requests
import json

BASE = "https://somekorean.com/api"

with open('/tmp/tokens.json') as f:
    t = json.load(f)

TOKEN = t['token']
TOKEN2 = t['token2']
USER2_ID = int(t['user2_id'])

def h1():
    return {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

def h2():
    return {"Authorization": f"Bearer {TOKEN2}", "Accept": "application/json", "Content-Type": "application/json"}

results = {}

print("="*60)
print("=== DM (1:1 MESSAGE) API TESTS ===")
print("="*60)

# 1. 쪽지 받은 함
print("\n[1] GET /api/messages/inbox (inbox)")
r = requests.get(f"{BASE}/messages/inbox", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
    results['dm_inbox'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['dm_inbox'] = 'FAIL'

# 2. 읽지 않은 메시지 수
print("\n[2] GET /api/messages/unread")
r = requests.get(f"{BASE}/messages/unread", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:100]}")
    results['dm_unread'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['dm_unread'] = 'FAIL'

# 3. 쪽지 보내기 (POST /api/messages)
print(f"\n[3] POST /api/messages (send DM to user {USER2_ID})")
payload = {"receiver_id": USER2_ID, "content": "안녕하세요! DM 테스트 메시지입니다."}
r = requests.post(f"{BASE}/messages", headers=h1(), json=payload, timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if r.status_code in [200, 201]:
        print(f"  Message ID: {data.get('id', 'N/A')}")
        msg_id = data.get('id')
        results['dm_send'] = 'PASS'
    else:
        print(f"  Error: {json.dumps(data)[:200]}")
        msg_id = None
        results['dm_send'] = 'FAIL'
except Exception as e:
    print(f"  Error: {e}, raw: {r.text[:100]}")
    msg_id = None
    results['dm_send'] = 'FAIL'

# 4. 자신에게 보내기 (400 예상)
print("\n[4] POST /api/messages to self (should fail)")
payload_self = {"receiver_id": 1, "content": "자기 자신에게"}
r = requests.post(f"{BASE}/messages", headers=h1(), json=payload_self, timeout=15)
print(f"  Status: {r.status_code} (expected 400)")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['dm_send_self'] = 'PASS' if r.status_code == 400 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['dm_send_self'] = 'FAIL'

# 5. 메시지 상세 보기
if msg_id:
    print(f"\n[5] GET /api/messages/{msg_id}")
    r = requests.get(f"{BASE}/messages/{msg_id}", headers=h1(), timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        data = r.json()
        print(f"  Content: {data.get('content', 'N/A')[:50] if isinstance(data, dict) else str(data)[:100]}")
        results['dm_show'] = 'PASS' if r.status_code == 200 else 'FAIL'
    except Exception as e:
        print(f"  Error: {e}")
        results['dm_show'] = 'FAIL'
else:
    print("\n[5] GET /api/messages/{id} - SKIP (no msg_id)")
    results['dm_show'] = 'SKIP'

print("\n" + "="*60)
print("=== ADDITIONAL BUG CHECKS ===")
print("="*60)

# Check match like with a fresh user (reset)
print("\n[6] Match like with different user ID (user2 likes user1)")
r = requests.post(f"{BASE}/match/like/1", headers=h2(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    is_match = data.get('is_match', False)
    print(f"  Is match: {is_match}")
    results['match_like_mutual'] = 'PASS' if r.status_code in [200, 201, 409] else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_like_mutual'] = 'FAIL'

# Check chat report
print("\n[7] POST /api/chat/report/{messageId}")
r = requests.post(f"{BASE}/chat/report/440", headers=h1(), json={"reason": "spam"}, timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['chat_report'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['chat_report'] = 'FAIL'

# Check if match block exists
print("\n[8] Match block feature check")
r = requests.post(f"{BASE}/match/block/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    if r.status_code == 404:
        print("  MISSING: Match block feature not implemented!")
        results['match_block'] = 'FAIL - NOT IMPLEMENTED'
    else:
        results['match_block'] = 'PASS'
except Exception as e:
    print(f"  Error: {e}")
    results['match_block'] = 'FAIL'

# Check PUT /api/match/profile (profile update)
print("\n[9] PUT /api/match/profile (update - check if PUT works)")
payload = {
    "nickname": "업데이트유저",
    "gender": "male",
    "birth_year": 1990,
    "bio": "수정된 프로필"
}
r = requests.put(f"{BASE}/match/profile", headers=h1(), json=payload, timeout=15)
print(f"  PUT Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    if r.status_code == 405:
        print("  BUG: PUT not supported, only POST - checking...")
        results['match_profile_put'] = 'INFO - only POST supported'
    else:
        results['match_profile_put'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['match_profile_put'] = 'FAIL'

print("\n" + "="*60)
print("=== ALL TEST RESULTS SUMMARY ===")
print("="*60)
for k, v in results.items():
    ok = "OK" if "PASS" in str(v) else ("--" if "SKIP" in str(v) else "XX")
    print(f"  [{ok}] {k}: {v}")

with open('/tmp/all_results.json', 'w') as f:
    json.dump(results, f)
