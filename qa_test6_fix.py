import paramiko
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

# Get token
cmd = 'cd /var/www/somekorean && php artisan tinker --execute="echo \\Tymon\\JWTAuth\\Facades\\JWTAuth::fromUser(App\\\\Models\\\\User::find(1));"'
stdin, stdout, stderr = ssh.exec_command(cmd)
token = stdout.read().decode().strip()
print(f"Token: {token[:60]}...")

def ssh_exec(command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

AUTH = f'Authorization: Bearer {token}'
BASE = "https://somekorean.com/api"

def api_call(method, path, data=None):
    url = f"{BASE}{path}"
    if data:
        json_str = json.dumps(data, ensure_ascii=False)
        write_cmd = f"cat > /tmp/req.json << 'JSONEOF'\n{json_str}\nJSONEOF"
        ssh_exec(write_cmd)
        cmd = f'curl -s -o /tmp/resp.json -w "%{{http_code}}" -X {method} -H "Accept: application/json" -H "Content-Type: application/json" -H "{AUTH}" -d @/tmp/req.json "{url}"'
    else:
        if method == "GET":
            cmd = f'curl -s -o /tmp/resp.json -w "%{{http_code}}" -H "Accept: application/json" -H "{AUTH}" "{url}"'
        else:
            cmd = f'curl -s -o /tmp/resp.json -w "%{{http_code}}" -X {method} -H "Accept: application/json" -H "Content-Type: application/json" -H "{AUTH}" "{url}"'
    status_out, _ = ssh_exec(cmd)
    status = status_out.strip()
    body_out, _ = ssh_exec("cat /tmp/resp.json")
    body = body_out.strip()
    return status, body

def tinker(php_code):
    cmd = f'cd /var/www/somekorean && php artisan tinker --execute="{php_code}"'
    out, err = ssh_exec(cmd)
    return out.strip()

cleanup_ids = {}

# ===== RE-TEST 5: POST /api/businesses/{business}/review (singular!) =====
print("\n=== Re-Test 5: POST /api/businesses/3/review ===")
s, b = api_call("POST", "/businesses/3/review", {"rating":5,"content":"좋은 업소입니다 테스트 리뷰"})
print(f"Status: {s}")
print(f"Body: {b[:200]}")
try:
    d = json.loads(b)
    cleanup_ids["review"] = d.get("data",{}).get("id") or d.get("review",{}).get("id") or d.get("id")
except: pass

# ===== RE-TEST 6: GET /api/businesses/3/reviews (check actual route) =====
print("\n=== Re-Test 6: GET /api/businesses/3/reviews ===")
s6, b6 = api_call("GET", "/businesses/3/reviews")
print(f"Status: {s6}")
print(f"Body: {b6[:200]}")
# If this returns HTML, try /review
if b6.startswith("<!DOCTYPE") or b6.startswith("<html"):
    print("Got HTML, trying /businesses/3/review instead...")
    s6b, b6b = api_call("GET", "/businesses/3/review")
    print(f"Status: {s6b}")
    print(f"Body: {b6b[:200]}")

# ===== RE-TEST 8: POST /api/businesses/{id}/claim with method field =====
# First register a new business for claiming
s, b = api_call("POST", "/businesses", {"name":"테스트 업소 QA6-fix","category":"restaurant","phone":"213-555-9999","address":"456 Test Ave, LA, CA","description":"클레임 테스트용 업소"})
print(f"\nNew biz for claim: {s} - {b[:150]}")
new_biz_id = None
try:
    d = json.loads(b)
    new_biz_id = d.get("business",{}).get("id") or d.get("data",{}).get("id") or d.get("id")
except: pass
cleanup_ids["business"] = new_biz_id

claim_target = new_biz_id or 3
print(f"\n=== Re-Test 8: POST /api/businesses/{claim_target}/claim ===")
s, b = api_call("POST", f"/businesses/{claim_target}/claim", {"method":"document","message":"제가 이 업소의 실제 소유자입니다"})
print(f"Status: {s}")
print(f"Body: {b[:200]}")
cleanup_ids["claim_biz"] = claim_target

# ===== RE-TEST 10: POST /api/qa with category_id =====
print("\n=== Re-Test 10: POST /api/qa ===")
s, b = api_call("POST", "/qa", {"title":"테스트 질문입니다 QA6","content":"이것은 테스트 질문입니다","category_id":1})
print(f"Status: {s}")
print(f"Body: {b[:200]}")
try:
    d = json.loads(b)
    cleanup_ids["qa"] = d.get("data",{}).get("id") or d.get("question",{}).get("id") or d.get("id")
except: pass

# ===== RE-TEST 13: QA like — check route (qa/answers/{id}/like) =====
# First get an answer ID to like
qa_id = cleanup_ids.get("qa")
if qa_id:
    # Answer the question first
    s_ans, b_ans = api_call("POST", f"/qa/{qa_id}/answers", {"content":"이것은 테스트 답변입니다 fix"})
    print(f"\nAnswer for like test: {s_ans}")
    try:
        d = json.loads(b_ans)
        ans_id = d.get("answer",{}).get("id") or d.get("data",{}).get("id") or d.get("id")
        cleanup_ids["answer"] = ans_id
    except:
        ans_id = None

    if ans_id:
        print(f"\n=== Re-Test 13: POST /api/qa/answers/{ans_id}/like ===")
        s, b = api_call("POST", f"/qa/answers/{ans_id}/like")
        print(f"Status: {s}")
        print(f"Body: {b[:200]}")
    else:
        print("No answer ID, trying qa/{id}/like with different method")
else:
    # Try with existing QA post
    print("\n=== Re-Test 13: Trying different like routes ===")
    # Try PUT
    s, b = api_call("PUT", "/qa/1/like")
    print(f"PUT /api/qa/1/like: {s} - {b[:100]}")
    # Try POST on answers
    s, b = api_call("POST", "/qa/answers/1/like")
    print(f"POST /api/qa/answers/1/like: {s} - {b[:100]}")

# ===== CLEANUP =====
print("\n\n=== CLEANUP ===")

if cleanup_ids.get("review"):
    r = tinker(f"App\\\\Models\\\\BusinessReview::find({cleanup_ids['review']})?->delete(); echo 'ok';")
    print(f"Delete review {cleanup_ids['review']}: {r}")

if cleanup_ids.get("answer"):
    r = tinker(f"App\\\\Models\\\\QaAnswer::find({cleanup_ids['answer']})?->delete(); echo 'ok';")
    print(f"Delete answer {cleanup_ids['answer']}: {r}")

if cleanup_ids.get("qa"):
    r = tinker(f"App\\\\Models\\\\QaQuestion::find({cleanup_ids['qa']})?->delete(); echo 'ok';")
    print(f"Delete qa {cleanup_ids['qa']}: {r}")

if cleanup_ids.get("claim_biz"):
    r = tinker(f"DB::table('business_claims')->where('business_id', {cleanup_ids['claim_biz']})->where('user_id', 1)->delete(); echo 'ok';")
    print(f"Delete claim: {r}")

if cleanup_ids.get("business"):
    r = tinker(f"App\\\\Models\\\\Business::find({cleanup_ids['business']})?->delete(); echo 'ok';")
    print(f"Delete business {cleanup_ids['business']}: {r}")

# Also clean up recipe like from first run (find correct table)
r = tinker("echo DB::select('SHOW TABLES LIKE \\'%like%\\'')[0]->{'Tables_in_somekorean (%like%)'} ?? 'none';")
print(f"Like tables: {r}")

# Try to clean recipe like with correct table
r = tinker("echo collect(DB::select(\\\"SHOW TABLES LIKE '%like%'\\\"))->implode(fn(\\$t) => array_values((array)\\$t)[0], ', ');")
print(f"Like tables: {r}")

ssh.close()
print("\nDone!")
