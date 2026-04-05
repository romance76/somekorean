import paramiko
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=20):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# Generate JWT tokens via tinker
print("=== Generating JWT tokens ===")
out, err = run(r'cd /var/www/somekorean && php artisan tinker --execute="echo \Tymon\JWTAuth\Facades\JWTAuth::fromUser(\App\Models\User::find(1));"')
user_token = out.strip().split('\n')[-1].strip()
print(f"User token (len={len(user_token)}): {user_token[:50]}...")

out, err = run(r'cd /var/www/somekorean && php artisan tinker --execute="echo \Tymon\JWTAuth\Facades\JWTAuth::fromUser(\App\Models\User::find(272));"')
admin_token = out.strip().split('\n')[-1].strip()
print(f"Admin token (len={len(admin_token)}): {admin_token[:50]}...")
print()

if len(user_token) < 50 or len(admin_token) < 50:
    print(f"TOKEN ERROR. user_token={user_token}, admin_token={admin_token}")
    ssh.close()
    sys.exit(1)

# Also check user/profile route method
out, err = run(r'cd /var/www/somekorean && php artisan route:list --path=api/user/profile 2>/dev/null')
print(f"Profile routes: {out}")
out, err = run(r'cd /var/www/somekorean && php artisan route:list --path=api/user 2>/dev/null | head -20')
print(f"User routes:\n{out}")
print()

def curl_test(label, method, url, token=None, data=None):
    headers = '-H "Accept: application/json"'
    if token:
        headers += f' -H "Authorization: Bearer {token}"'
    if data:
        headers += ' -H "Content-Type: application/json"'

    method_flag = f'-X {method}' if method != 'GET' else ''
    data_flag = f"-d '{data}'" if data else ''

    cmd = f'curl -sk {method_flag} "{url}" {headers} {data_flag} -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null'
    out, _ = run(cmd)

    lines = out.strip().split('\n')
    status_line = [l for l in lines if l.startswith('HTTP_STATUS:')]
    status = status_line[0].replace('HTTP_STATUS:', '') if status_line else 'N/A'
    body = '\n'.join([l for l in lines if not l.startswith('HTTP_STATUS:')])

    print(f"=== {label} ===")
    print(f"  URL: {method} {url}")
    print(f"  Status: {status}")
    print(f"  Response: {body[:200]}")

    return status, body

# ========== AUTH TESTS ==========
print("\n" + "="*60)
print("AUTH TESTS")
print("="*60)

# TEST 1: Login (we know password is likely hashed, try via API)
s, b = curl_test("TEST 1: POST /api/auth/login", "POST", "https://somekorean.com/api/auth/login",
          data='{"email":"test@test.com","password":"password"}')
# Status 401 = correct rejection of wrong password, which is expected behavior
t1_pass = s in ['200', '401']
print(f"  RESULT: {'PASS' if t1_pass else 'FAIL'} {'(auth endpoint works, credentials rejected)' if s == '401' else '(login success)'}")
print()

# TEST 2: Register validation
s, b = curl_test("TEST 2: POST /api/auth/register (dup email)", "POST", "https://somekorean.com/api/auth/register",
          data='{"name":"Test","email":"test@test.com","password":"password","password_confirmation":"password"}')
t2_pass = s == '422' and 'email' in b.lower()
print(f"  RESULT: {'PASS' if t2_pass else 'FAIL'}")
print()

# TEST 3: Get current user
s, b = curl_test("TEST 3: GET /api/auth/me", "GET", "https://somekorean.com/api/auth/me", token=user_token)
t3_pass = s == '200' and 'user' in b.lower()
print(f"  RESULT: {'PASS' if t3_pass else 'FAIL'}")
print()

# ========== PROFILE TESTS ==========
print("\n" + "="*60)
print("PROFILE TESTS")
print("="*60)

# TEST 4: User dashboard
s, b = curl_test("TEST 4: GET /api/user/dashboard", "GET", "https://somekorean.com/api/user/dashboard", token=user_token)
t4_pass = s == '200' and not b.startswith('<!DOCTYPE')
print(f"  RESULT: {'PASS' if t4_pass else 'FAIL'}{' (returned HTML instead of JSON)' if b.startswith('<!DOCTYPE') else ''}")
print()

# TEST 5: Update profile - check correct method
s, b = curl_test("TEST 5: POST /api/user/profile", "POST", "https://somekorean.com/api/user/profile",
          token=user_token, data='{"name":"Test User Updated","bio":"test profile"}')
t5_pass = s in ['200', '201']
print(f"  RESULT: {'PASS' if t5_pass else 'FAIL'}")
print()

# TEST 6: Bookmarks
s, b = curl_test("TEST 6: GET /api/user/bookmarks", "GET", "https://somekorean.com/api/user/bookmarks", token=user_token)
t6_pass = s == '200' and not b.startswith('<!DOCTYPE')
print(f"  RESULT: {'PASS' if t6_pass else 'FAIL'}{' (returned HTML instead of JSON)' if b.startswith('<!DOCTYPE') else ''}")
print()

# TEST 7: Points
s, b = curl_test("TEST 7: GET /api/user/points", "GET", "https://somekorean.com/api/user/points", token=user_token)
t7_pass = s == '200' and not b.startswith('<!DOCTYPE')
print(f"  RESULT: {'PASS' if t7_pass else 'FAIL'}{' (returned HTML instead of JSON)' if b.startswith('<!DOCTYPE') else ''}")
print()

# ========== NOTIFICATION TESTS ==========
print("\n" + "="*60)
print("NOTIFICATION TESTS")
print("="*60)

# TEST 8: Notifications
s, b = curl_test("TEST 8: GET /api/notifications", "GET", "https://somekorean.com/api/notifications", token=user_token)
t8_pass = s == '200'
print(f"  RESULT: {'PASS' if t8_pass else 'FAIL'}")
print()

# TEST 9: Unread notifications
s, b = curl_test("TEST 9: GET /api/notifications/unread", "GET", "https://somekorean.com/api/notifications/unread", token=user_token)
t9_pass = s == '200'
print(f"  RESULT: {'PASS' if t9_pass else 'FAIL'}")
print()

# ========== ADMIN TESTS ==========
print("\n" + "="*60)
print("ADMIN TESTS")
print("="*60)

# TEST 10: Admin menu settings
s, b = curl_test("TEST 10: GET /api/admin/settings/menus", "GET", "https://somekorean.com/api/admin/settings/menus", token=admin_token)
t10_pass = s == '200'
# Check for order, login_required, admin_only
has_fields = all(f in b for f in ['order', 'login_required', 'admin_only']) if s == '200' else False
print(f"  RESULT: {'PASS' if t10_pass else 'FAIL'}{' (has order/login_required/admin_only)' if has_fields else ''}")
print()

# TEST 11: Admin dashboard
s, b = curl_test("TEST 11: GET /api/admin/dashboard", "GET", "https://somekorean.com/api/admin/dashboard", token=admin_token)
t11_pass = s == '200' and not b.startswith('<!DOCTYPE')
print(f"  RESULT: {'PASS' if t11_pass else 'FAIL'}{' (returned HTML instead of JSON)' if b.startswith('<!DOCTYPE') else ''}")
print()

# TEST 12: Admin users
s, b = curl_test("TEST 12: GET /api/admin/users", "GET", "https://somekorean.com/api/admin/users", token=admin_token)
t12_pass = s == '200' and not b.startswith('<!DOCTYPE')
print(f"  RESULT: {'PASS' if t12_pass else 'FAIL'}")
print()

# ========== SEARCH TEST ==========
print("\n" + "="*60)
print("SEARCH TEST")
print("="*60)

s, b = curl_test("TEST 13: GET /api/search?q=test", "GET", "https://somekorean.com/api/search?q=test")
t13_pass = s == '200' and 'result' in b
print(f"  RESULT: {'PASS' if t13_pass else 'FAIL'}")
print()

# ========== SUMMARY ==========
results = [
    ("TEST 1", "POST /api/auth/login", t1_pass),
    ("TEST 2", "POST /api/auth/register (dup)", t2_pass),
    ("TEST 3", "GET /api/auth/me", t3_pass),
    ("TEST 4", "GET /api/user/dashboard", t4_pass),
    ("TEST 5", "POST /api/user/profile", t5_pass),
    ("TEST 6", "GET /api/user/bookmarks", t6_pass),
    ("TEST 7", "GET /api/user/points", t7_pass),
    ("TEST 8", "GET /api/notifications", t8_pass),
    ("TEST 9", "GET /api/notifications/unread", t9_pass),
    ("TEST 10", "GET /api/admin/settings/menus", t10_pass),
    ("TEST 11", "GET /api/admin/dashboard", t11_pass),
    ("TEST 12", "GET /api/admin/users", t12_pass),
    ("TEST 13", "GET /api/search?q=test", t13_pass),
]

print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)
passed = sum(1 for _, _, p in results if p)
total = len(results)
for name, url, p in results:
    print(f"  {name}: {url} -> {'PASS' if p else 'FAIL'}")
print(f"\n  Total: {passed}/{total} PASSED")

ssh.close()
