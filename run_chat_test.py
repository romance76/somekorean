#!/usr/bin/env python3
"""채팅/매칭/친구 심층 테스트 스크립트"""
import socket
import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE = "https://68.183.60.70"
T1 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovLzY4LjE4My42MC43MC9hcGkvYXV0aC9yZWdpc3RlciIsImlhdCI6MTc3NDk2MjMyOSwiZXhwIjoxNzc0OTY1OTI5LCJuYmYiOjE3NzQ5NjIzMjksImp0aSI6InBpcnBSbEpXOWxyZHhFbGIiLCJzdWIiOiIyODEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.i1nwB9EOqGLPebXAxOflDZgPOUjv7t4_L80SDtWhMgA"
T2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovLzY4LjE4My42MC43MC9hcGkvYXV0aC9yZWdpc3RlciIsImlhdCI6MTc3NDk2MjMzNSwiZXhwIjoxNzc0OTY1OTM1LCJuYmYiOjE3NzQ5NjIzMzUsImp0aSI6InFtYXg1OWFIU21hcmJsMTEiLCJzdWIiOiIyODIiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.b1N7_XxgppHLA3-wSgnmfJ6MBR0uUg3lYxAiItqt_Gs"
U1 = 281
U2 = 282

import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

results = {}

def api(method, path, token=None, data=None):
    url = BASE + path
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, raw[:200]
    except Exception as e:
        return 0, str(e)

def P(name, status, detail=""):
    mark = "PASS" if status else "FAIL"
    print(f"  [{mark}] {name}: {detail}")
    results[name] = status

print("\n" + "="*60)
print("채팅 심층 테스트")
print("="*60)

# [1] GET /api/chat/rooms
code, data = api("GET", "/api/chat/rooms", T1)
if code == 200 and isinstance(data, list):
    slugs = [r.get("slug") for r in data]
    has_slug = all(s is not None for s in slugs)
    P("[1] GET chat/rooms (slug 포함)", code==200 and has_slug,
      f"HTTP {code}, {len(data)}개 방, slugs: {slugs[:3]}")
else:
    P("[1] GET chat/rooms", False, f"HTTP {code}")

# [2] GET /api/chat/rooms/open-chat
code, data = api("GET", "/api/chat/rooms/open-chat", T1)
if code == 200:
    room = data.get("room", {})
    msgs = data.get("messages", [])
    P("[2] GET chat/rooms/open-chat", True,
      f"HTTP {code}, 방:{room.get('name','?')}, 메시지:{len(msgs)}개")
else:
    P("[2] GET chat/rooms/open-chat", False, f"HTTP {code}, {str(data)[:100]}")

# [3] POST /api/chat/rooms/open-chat/messages
code, data = api("POST", "/api/chat/rooms/open-chat/messages", T1, {"message": "테스트 메시지입니다"})
if code in (200, 201):
    P("[3] POST chat messages (전송)", True,
      f"HTTP {code}, id:{data.get('id')}, msg:{str(data.get('message',''))[:30]}")
elif code == 500:
    P("[3] POST chat messages (전송)", False,
      f"HTTP 500 - Broadcast 에러 (Reverb 미작동 가능성)")
else:
    P("[3] POST chat messages (전송)", False, f"HTTP {code}, {str(data)[:100]}")

# [4] POST /api/chat/rooms (새 채팅방 생성 - 일반유저)
code, data = api("POST", "/api/chat/rooms", T1, {"name":"테스트방","slug":"test-room-281","type":"open"})
if code in (200, 201):
    P("[4] POST chat/rooms (방 생성)", True, f"HTTP {code}, slug:{data.get('slug')}")
elif code == 401:
    P("[4] POST chat/rooms (방 생성)", False, f"HTTP 401 - 인증 필요/권한 없음")
elif code == 405:
    P("[4] POST chat/rooms (방 생성)", False, f"HTTP 405 - 일반유저 라우트 없음 (어드민 전용)")
else:
    P("[4] POST chat/rooms (방 생성)", False, f"HTTP {code}, {str(data)[:100]}")

# [5] GET /api/chat/rooms/open-chat/search?q=test
code, data = api("GET", "/api/chat/rooms/open-chat/search?q=테스트", T1)
if code == 200:
    P("[5] GET chat search", True, f"HTTP {code}, 결과:{len(data)}개")
else:
    P("[5] GET chat search", False, f"HTTP {code}, {str(data)[:100]}")

# [6] POST /api/chat/block/{userId}
code, data = api("POST", f"/api/chat/block/{U2}", T1)
P("[6] POST chat/block", code==200, f"HTTP {code}, {str(data)[:80]}")

# [7] DELETE /api/chat/block/{userId}
code, data = api("DELETE", f"/api/chat/block/{U2}", T1)
P("[7] DELETE chat/block (해제)", code==200, f"HTTP {code}, {str(data)[:80]}")

# [8] POST /api/chat/report/{messageId} - 메시지 ID 1로 시도
code, data = api("POST", "/api/chat/report/249", T1, {"reason":"spam"})
P("[8] POST chat/report", code==200, f"HTTP {code}, {str(data)[:80]}")

print("\n" + "="*60)
print("WebSocket / Reverb 상태")
print("="*60)

# 8080 포트 열림 확인
s = socket.socket()
s.settimeout(5)
try:
    r = s.connect_ex(("68.183.60.70", 8080))
    if r == 0:
        P("WebSocket 8080 포트", True, "OPEN")
    else:
        P("WebSocket 8080 포트", False, f"CLOSED (errno={r})")
    s.close()
except Exception as e:
    P("WebSocket 8080 포트", False, str(e))

print("\n" + "="*60)
print("매칭 테스트")
print("="*60)

# [M1] GET /api/match/profile (내 프로필)
code, data = api("GET", "/api/match/profile", T1)
P("[M1] GET match/profile (내 프로필)", code in (200, 404),
  f"HTTP {code}, {str(data)[:100]}")

# [M2] GET /api/match/browse
code, data = api("GET", "/api/match/browse", T1)
if code == 200:
    count = len(data) if isinstance(data, list) else data.get("total", "?")
    P("[M2] GET match/browse", True, f"HTTP {code}, {count}개 프로필")
else:
    P("[M2] GET match/browse", False, f"HTTP {code}, {str(data)[:100]}")

# [M3] POST /api/match/profile (프로필 생성)
code, data = api("POST", "/api/match/profile", T1, {
    "age": "30", "gender": "male", "region": "LA", "bio": "테스트 프로필"
})
P("[M3] POST match/profile", code in (200, 201, 422),
  f"HTTP {code}, {str(data)[:100]}")

# [M4] POST /api/match/like/{userId}
code, data = api("POST", f"/api/match/like/{U2}", T1)
P("[M4] POST match/like", code in (200, 201), f"HTTP {code}, {str(data)[:80]}")

# [M5] GET /api/match/likes (받은 좋아요)
code, data = api("GET", "/api/match/likes", T1)
P("[M5] GET match/likes", code == 200, f"HTTP {code}, {str(data)[:100]}")

# [M6] GET /api/match/matches
code, data = api("GET", "/api/match/matches", T1)
P("[M6] GET match/matches", code == 200, f"HTTP {code}, {str(data)[:100]}")

print("\n" + "="*60)
print("친구 테스트")
print("="*60)

# [F1] GET /api/friends
code, data = api("GET", "/api/friends", T1)
P("[F1] GET friends", code == 200, f"HTTP {code}, {str(data)[:100]}")

# [F2] GET /api/friends/search?q=Test
code, data = api("GET", "/api/friends/search?q=Test", T1)
P("[F2] GET friends/search", code == 200, f"HTTP {code}, {len(data) if isinstance(data,list) else '?'}개 결과")

# [F3] POST /api/friends/request/{userId}
code, data = api("POST", f"/api/friends/request/{U2}", T1)
P("[F3] POST friends/request", code in (200, 201), f"HTTP {code}, {str(data)[:80]}")

# [F4] POST /api/friends/accept/{userId} (U2가 U1 수락)
code, data = api("POST", f"/api/friends/accept/{U1}", T2)
P("[F4] POST friends/accept (상대방)", code in (200, 201), f"HTTP {code}, {str(data)[:80]}")

# [F5] GET /api/friends (친구 확인)
code, data = api("GET", "/api/friends", T1)
P("[F5] GET friends (수락 후)", code == 200,
  f"HTTP {code}, 친구수:{len(data) if isinstance(data,list) else '?'}")

# [F6] POST /api/friends/reject/{userId}
# 먼저 U1이 다른 요청 보내고 U2가 거절
code, data = api("POST", f"/api/friends/reject/{U1}", T2)
P("[F6] POST friends/reject", code in (200, 201, 404), f"HTTP {code}, {str(data)[:80]}")

# [F7] DELETE /api/friends/{userId}
code, data = api("DELETE", f"/api/friends/{U2}", T1)
P("[F7] DELETE friends", code == 200, f"HTTP {code}, {str(data)[:80]}")

print("\n" + "="*60)
print("DM (직접 메시지) 테스트")
print("="*60)

# [D1] GET /api/messages/inbox
code, data = api("GET", "/api/messages/inbox", T1)
P("[D1] GET messages/inbox", code == 200, f"HTTP {code}, {str(data)[:100]}")

# [D2] POST /api/messages
code, data = api("POST", "/api/messages", T1, {
    "receiver_id": str(U2), "content": "안녕하세요 DM 테스트"
})
P("[D2] POST messages (DM 전송)", code in (200, 201), f"HTTP {code}, {str(data)[:100]}")

# [D3] GET /api/messages/unread
code, data = api("GET", "/api/messages/unread", T1)
P("[D3] GET messages/unread", code == 200, f"HTTP {code}, {str(data)[:80]}")

print("\n" + "="*60)
print("결과 요약")
print("="*60)
passed = sum(1 for v in results.values() if v)
total = len(results)
print(f"PASS: {passed}/{total}")
print(f"FAIL: {total-passed}/{total}")
failed = [k for k, v in results.items() if not v]
if failed:
    print(f"\n실패 항목:")
    for f in failed:
        print(f"  - {f}")
