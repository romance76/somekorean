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
print("=== CHAT API TESTS ===")
print("="*60)

# 1. 채팅방 목록 (GET /api/chat/rooms)
print("\n[1] GET /api/chat/rooms")
r = requests.get(f"{BASE}/chat/rooms", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    if isinstance(data, list):
        print(f"  Rooms count: {len(data)}")
        if data:
            print(f"  First room: {data[0].get('name', 'N/A')} (slug: {data[0].get('slug', 'N/A')})")
            first_slug = data[0].get('slug', '')
        else:
            first_slug = ''
    else:
        print(f"  Response: {json.dumps(data)[:200]}")
        first_slug = ''
    results['chat_rooms_list'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    first_slug = ''
    results['chat_rooms_list'] = 'FAIL'

# 2. 채팅방 입장 (GET /api/chat/rooms/{slug})
print(f"\n[2] GET /api/chat/rooms/{{slug}} (slug={first_slug})")
if first_slug:
    r = requests.get(f"{BASE}/chat/rooms/{first_slug}", headers=h1(), timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        data = r.json()
        if 'room' in data:
            print(f"  Room: {data['room'].get('name', 'N/A')}")
            print(f"  Messages count: {len(data.get('messages', []))}")
            results['chat_room_enter'] = 'PASS'
        else:
            print(f"  Response: {json.dumps(data)[:200]}")
            results['chat_room_enter'] = 'FAIL'
    except Exception as e:
        print(f"  Error: {e}")
        results['chat_room_enter'] = 'FAIL'
else:
    print("  SKIP - no rooms found")
    results['chat_room_enter'] = 'SKIP'

# 3. 메시지 조회 (GET /api/chat/rooms/{slug}/messages)
print(f"\n[3] GET /api/chat/rooms/{{slug}}/messages")
if first_slug:
    r = requests.get(f"{BASE}/chat/rooms/{first_slug}/messages", headers=h1(), timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        data = r.json()
        print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
        results['chat_messages'] = 'PASS' if r.status_code == 200 else 'FAIL'
    except Exception as e:
        print(f"  Error: {e}")
        results['chat_messages'] = 'FAIL'
else:
    results['chat_messages'] = 'SKIP'

# 4. 메시지 전송 (POST /api/chat/rooms/{slug}/messages)
print(f"\n[4] POST /api/chat/rooms/{{slug}}/messages (send message)")
if first_slug:
    payload = {"message": "테스트 메시지입니다 - API Test"}
    r = requests.post(f"{BASE}/chat/rooms/{first_slug}/messages", headers=h1(), json=payload, timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        data = r.json()
        if r.status_code in [200, 201]:
            print(f"  Message ID: {data.get('id', 'N/A')}")
            print(f"  Message: {data.get('message', 'N/A')[:50]}")
            results['chat_send_message'] = 'PASS'
        else:
            print(f"  Response: {json.dumps(data)[:300]}")
            results['chat_send_message'] = 'FAIL'
    except Exception as e:
        print(f"  Error: {e}, Response: {r.text[:200]}")
        results['chat_send_message'] = 'FAIL'
else:
    results['chat_send_message'] = 'SKIP'

# 5. 채팅 검색 (GET /api/chat/rooms/{slug}/search)
print(f"\n[5] GET /api/chat/rooms/{{slug}}/search?q=테스트")
if first_slug:
    r = requests.get(f"{BASE}/chat/rooms/{first_slug}/search?q=테스트", headers=h1(), timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        data = r.json()
        print(f"  Results: {len(data) if isinstance(data, list) else data}")
        results['chat_search'] = 'PASS' if r.status_code == 200 else 'FAIL'
    except Exception as e:
        print(f"  Error: {e}")
        results['chat_search'] = 'FAIL'
else:
    results['chat_search'] = 'SKIP'

# 6. 유저 차단 (POST /api/chat/block/{userId})
print(f"\n[6] POST /api/chat/block/{{userId}} (block user)")
r = requests.post(f"{BASE}/chat/block/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['chat_block'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['chat_block'] = 'FAIL'

# 7. 유저 차단 해제 (DELETE /api/chat/block/{userId})
print(f"\n[7] DELETE /api/chat/block/{{userId}} (unblock user)")
r = requests.delete(f"{BASE}/chat/block/{USER2_ID}", headers=h1(), timeout=15)
print(f"  Status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:200]}")
    results['chat_unblock'] = 'PASS' if r.status_code == 200 else 'FAIL'
except Exception as e:
    print(f"  Error: {e}")
    results['chat_unblock'] = 'FAIL'

print("\n" + "="*60)
print("=== CHAT TEST RESULTS ===")
print("="*60)
for k, v in results.items():
    status_icon = "OK" if v == 'PASS' else ("--" if v == 'SKIP' else "XX")
    print(f"  [{status_icon}] {k}: {v}")

# Save results
with open('/tmp/chat_results.json', 'w') as f:
    json.dump({'results': results, 'first_slug': first_slug}, f)
