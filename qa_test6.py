import paramiko
import json
import re

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
        # Write JSON body to temp file to avoid shell escaping issues
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

results = []
cleanup_ids = {}

# Test 1: GET /api/businesses
s, b = api_call("GET", "/businesses")
results.append(("1", "GET", "/api/businesses", s, b[:200]))
print(f"Test 1: {s}")

biz_id = 1
try:
    d = json.loads(b)
    if "data" in d:
        items = d["data"] if isinstance(d["data"], list) else d["data"].get("data", [])
        if items:
            biz_id = items[0]["id"]
except:
    pass
print(f"biz_id={biz_id}")

# Test 2: category filter
s, b = api_call("GET", "/businesses?category=restaurant")
results.append(("2", "GET", "/api/businesses?category=restaurant", s, b[:200]))
print(f"Test 2: {s}")

# Test 3: region filter
s, b = api_call("GET", "/businesses?region=CA")
results.append(("3", "GET", "/api/businesses?region=CA", s, b[:200]))
print(f"Test 3: {s}")

# Test 4: business detail
s, b = api_call("GET", f"/businesses/{biz_id}")
results.append(("4", "GET", f"/api/businesses/{biz_id}", s, b[:200]))
print(f"Test 4: {s}")

# Test 5: add review
s, b = api_call("POST", f"/businesses/{biz_id}/reviews", {"rating":5,"content":"좋은 업소입니다 테스트 리뷰"})
results.append(("5", "POST", f"/api/businesses/{biz_id}/reviews", s, b[:200]))
print(f"Test 5: {s} - {b[:120]}")
try:
    d = json.loads(b)
    cleanup_ids["review"] = d.get("data",{}).get("id") or d.get("id")
except: pass

# Test 6: list reviews
s, b = api_call("GET", f"/businesses/{biz_id}/reviews")
results.append(("6", "GET", f"/api/businesses/{biz_id}/reviews", s, b[:200]))
print(f"Test 6: {s}")

# Test 7: register business
s, b = api_call("POST", "/businesses", {"name":"테스트 업소 QA6","category":"restaurant","phone":"213-555-1234","address":"123 Test St, LA, CA","description":"테스트 업소입니다"})
results.append(("7", "POST", "/api/businesses", s, b[:200]))
print(f"Test 7: {s} - {b[:120]}")
try:
    d = json.loads(b)
    cleanup_ids["business"] = d.get("data",{}).get("id") or d.get("id")
except: pass

# Test 8: claim ownership
claim_biz = cleanup_ids.get("business") or biz_id
s, b = api_call("POST", f"/businesses/{claim_biz}/claim", {"message":"제가 이 업소의 실제 소유자입니다"})
results.append(("8", "POST", f"/api/businesses/{claim_biz}/claim", s, b[:200]))
print(f"Test 8: {s} - {b[:120]}")
cleanup_ids["claim_biz"] = claim_biz

# Test 9: list QA
s, b = api_call("GET", "/qa")
results.append(("9", "GET", "/api/qa", s, b[:200]))
print(f"Test 9: {s}")

# Test 10: create question
s, b = api_call("POST", "/qa", {"title":"테스트 질문입니다 QA6","content":"이것은 테스트 질문입니다","category":"general"})
results.append(("10", "POST", "/api/qa", s, b[:200]))
print(f"Test 10: {s} - {b[:120]}")
try:
    d = json.loads(b)
    cleanup_ids["qa"] = d.get("data",{}).get("id") or d.get("id")
except: pass

qa_id = cleanup_ids.get("qa") or 1

# Test 11: question detail
s, b = api_call("GET", f"/qa/{qa_id}")
results.append(("11", "GET", f"/api/qa/{qa_id}", s, b[:200]))
print(f"Test 11: {s}")

# Test 12: answer question
s, b = api_call("POST", f"/qa/{qa_id}/answers", {"content":"이것은 테스트 답변입니다"})
results.append(("12", "POST", f"/api/qa/{qa_id}/answers", s, b[:200]))
print(f"Test 12: {s} - {b[:120]}")
try:
    d = json.loads(b)
    cleanup_ids["answer"] = d.get("data",{}).get("id") or d.get("id")
except: pass

# Test 13: like question
s, b = api_call("POST", f"/qa/{qa_id}/like")
results.append(("13", "POST", f"/api/qa/{qa_id}/like", s, b[:200]))
print(f"Test 13: {s} - {b[:120]}")

# Test 14: list recipes
s, b = api_call("GET", "/recipes")
results.append(("14", "GET", "/api/recipes", s, b[:200]))
print(f"Test 14: {s}")

recipe_id = 1
try:
    d = json.loads(b)
    items = d.get("data", [])
    if isinstance(items, dict):
        items = items.get("data", [])
    if items:
        recipe_id = items[0]["id"]
except: pass
print(f"recipe_id={recipe_id}")

# Test 15: recipe detail
s, b = api_call("GET", f"/recipes/{recipe_id}")
results.append(("15", "GET", f"/api/recipes/{recipe_id}", s, b[:200]))
print(f"Test 15: {s}")

# Test 16: like recipe
s, b = api_call("POST", f"/recipes/{recipe_id}/like")
results.append(("16", "POST", f"/api/recipes/{recipe_id}/like", s, b[:200]))
print(f"Test 16: {s} - {b[:120]}")

# Test 17: comment on recipe
s, b = api_call("POST", f"/recipes/{recipe_id}/comments", {"content":"맛있는 레시피네요!","rating":5})
results.append(("17", "POST", f"/api/recipes/{recipe_id}/comments", s, b[:200]))
print(f"Test 17: {s} - {b[:120]}")
try:
    d = json.loads(b)
    cleanup_ids["recipe_comment"] = d.get("data",{}).get("id") or d.get("id")
except: pass

# Test 18: list shorts
s, b = api_call("GET", "/shorts")
results.append(("18", "GET", "/api/shorts", s, b[:200]))
print(f"Test 18: {s}")
has_chinese = bool(re.findall(r'[\u4e00-\u9fff]', b))
print(f"Chinese chars in shorts: {has_chinese}")

# Test 19: shorts feed
s, b = api_call("GET", "/shorts/feed")
results.append(("19", "GET", "/api/shorts/feed", s, b[:200]))
print(f"Test 19: {s}")

# ========== CLEANUP ==========
print("\n=== CLEANUP ===")

if cleanup_ids.get("review"):
    r = tinker(f"App\\\\Models\\\\BusinessReview::find({cleanup_ids['review']})?->delete(); echo 'ok';")
    print(f"Delete review {cleanup_ids['review']}: {r}")

if cleanup_ids.get("answer"):
    r = tinker(f"App\\\\Models\\\\QaAnswer::find({cleanup_ids['answer']})?->delete(); echo 'ok';")
    print(f"Delete answer {cleanup_ids['answer']}: {r}")

if cleanup_ids.get("qa"):
    r = tinker(f"DB::table('qa_likes')->where('qa_question_id', {cleanup_ids['qa']})->where('user_id', 1)->delete(); echo 'ok';")
    print(f"Delete qa like: {r}")
    r = tinker(f"App\\\\Models\\\\QaQuestion::find({cleanup_ids['qa']})?->delete(); echo 'ok';")
    print(f"Delete qa {cleanup_ids['qa']}: {r}")

if cleanup_ids.get("claim_biz"):
    r = tinker(f"DB::table('business_claims')->where('business_id', {cleanup_ids['claim_biz']})->where('user_id', 1)->delete(); echo 'ok';")
    print(f"Delete claim: {r}")

if cleanup_ids.get("business"):
    r = tinker(f"App\\\\Models\\\\Business::find({cleanup_ids['business']})?->delete(); echo 'ok';")
    print(f"Delete business {cleanup_ids['business']}: {r}")

if recipe_id:
    r = tinker(f"DB::table('recipe_likes')->where('recipe_id', {recipe_id})->where('user_id', 1)->delete(); echo 'ok';")
    print(f"Delete recipe like: {r}")

if cleanup_ids.get("recipe_comment"):
    r = tinker(f"App\\\\Models\\\\RecipeComment::find({cleanup_ids['recipe_comment']})?->delete(); echo 'ok';")
    print(f"Delete recipe comment: {r}")

# ========== FINAL REPORT ==========
print("\n")
print("=" * 130)
print(f"{'#':<5} {'Method':<7} {'Endpoint':<48} {'Status':<7} {'Result':<6} {'Response Snippet'}")
print("=" * 130)
for num, method, url, status, snippet in results:
    s = status.strip()
    pf = "PASS" if s.startswith("2") else "FAIL"
    snip = snippet.replace('\n', ' ')[:100]
    print(f"{num:<5} {method:<7} {url:<48} {s:<7} {pf:<6} {snip}")
print("=" * 130)
print(f"Chinese shorts check: {'FAIL - Chinese found' if has_chinese else 'PASS - No Chinese'}")
total_pass = sum(1 for _, _, _, s, _ in results if s.strip().startswith("2"))
total_fail = len(results) - total_pass
print(f"Total: {total_pass} PASS / {total_fail} FAIL out of {len(results)} tests")

ssh.close()
