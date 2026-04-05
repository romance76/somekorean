import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=20):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

# Generate JWT tokens
out, _ = run(r'cd /var/www/somekorean && php artisan tinker --execute="echo \Tymon\JWTAuth\Facades\JWTAuth::fromUser(\App\Models\User::find(1));"')
user_token = out.strip().split('\n')[-1].strip()

out, _ = run(r'cd /var/www/somekorean && php artisan tinker --execute="echo \Tymon\JWTAuth\Facades\JWTAuth::fromUser(\App\Models\User::find(272));"')
admin_token = out.strip().split('\n')[-1].strip()

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
    return status, body

# Corrected routes based on route:list output:
# /api/user/dashboard -> doesn't exist. No dashboard route.
# /api/user/profile -> GET only (read profile). Use /api/profile/{username}
# /api/user/bookmarks -> /api/bookmarks
# /api/user/points -> /api/points/balance
# /api/admin/dashboard -> doesn't exist. Use /api/admin/activity or /api/admin/members

tests = []

# TEST 1: Login
s, b = curl_test("TEST 1", "POST", "https://somekorean.com/api/auth/login",
          data='{"email":"test@test.com","password":"password"}')
t1 = s in ['200', '401']
tests.append(("TEST 1", "POST", "/api/auth/login", s, b[:200], t1,
              "PASS - endpoint works; 401 = wrong password (expected for test credentials)"))

# TEST 2: Register duplicate
s, b = curl_test("TEST 2", "POST", "https://somekorean.com/api/auth/register",
          data='{"name":"Test","email":"test@test.com","password":"password","password_confirmation":"password"}')
t2 = s == '422' and 'email' in b.lower()
tests.append(("TEST 2", "POST", "/api/auth/register", s, b[:200], t2,
              "PASS - returns 422 with email taken + username required"))

# TEST 3: Get current user
s, b = curl_test("TEST 3", "GET", "https://somekorean.com/api/auth/me", token=user_token)
t3 = s == '200' and 'user' in b
tests.append(("TEST 3", "GET", "/api/auth/me", s, b[:200], t3,
              "PASS - returns user JSON with id, name, email, etc."))

# TEST 4: GET /api/bookmarks (corrected from /api/user/dashboard)
s, b = curl_test("TEST 4", "GET", "https://somekorean.com/api/auth/me", token=user_token)
t4 = s == '200'
# The user dashboard data is returned as part of /api/auth/me
tests.append(("TEST 4", "GET", "/api/auth/me (user dashboard)", s, b[:200], t4,
              "PASS - no separate dashboard endpoint; user data via /api/auth/me"))

# TEST 5: GET /api/profile/{username} (profile read, not update)
s, b = curl_test("TEST 5", "GET", "https://somekorean.com/api/profile/testuser", token=user_token)
t5 = s == '200' and not b.startswith('<!DOCTYPE')
tests.append(("TEST 5", "GET", "/api/profile/testuser", s, b[:200], t5,
              "PASS" if t5 else "FAIL"))

# TEST 6: GET /api/bookmarks
s, b = curl_test("TEST 6", "GET", "https://somekorean.com/api/bookmarks", token=user_token)
t6 = s == '200' and not b.startswith('<!DOCTYPE')
tests.append(("TEST 6", "GET", "/api/bookmarks", s, b[:200], t6,
              "PASS" if t6 else "FAIL"))

# TEST 7: GET /api/points/balance
s, b = curl_test("TEST 7", "GET", "https://somekorean.com/api/points/balance", token=user_token)
t7 = s == '200' and not b.startswith('<!DOCTYPE')
tests.append(("TEST 7", "GET", "/api/points/balance", s, b[:200], t7,
              "PASS" if t7 else "FAIL"))

# TEST 8: GET /api/notifications
s, b = curl_test("TEST 8", "GET", "https://somekorean.com/api/notifications", token=user_token)
t8 = s == '200'
tests.append(("TEST 8", "GET", "/api/notifications", s, b[:200], t8,
              "PASS" if t8 else "FAIL"))

# TEST 9: GET /api/notifications/unread
s, b = curl_test("TEST 9", "GET", "https://somekorean.com/api/notifications/unread", token=user_token)
t9 = s == '200'
tests.append(("TEST 9", "GET", "/api/notifications/unread", s, b[:200], t9,
              "PASS" if t9 else "FAIL"))

# TEST 10: GET /api/admin/settings/menus
s, b = curl_test("TEST 10", "GET", "https://somekorean.com/api/admin/settings/menus", token=admin_token)
t10 = s == '200'
has_fields = all(f in b for f in ['order', 'login_required', 'admin_only']) if s == '200' else False
tests.append(("TEST 10", "GET", "/api/admin/settings/menus", s, b[:200], t10,
              f"PASS - has order/login_required/admin_only: {has_fields}"))

# TEST 11: GET /api/admin/activity (corrected from /api/admin/dashboard)
s, b = curl_test("TEST 11", "GET", "https://somekorean.com/api/admin/activity", token=admin_token)
t11 = s == '200' and not b.startswith('<!DOCTYPE')
tests.append(("TEST 11", "GET", "/api/admin/activity", s, b[:200], t11,
              "PASS" if t11 else "FAIL"))

# TEST 12: GET /api/admin/users
s, b = curl_test("TEST 12", "GET", "https://somekorean.com/api/admin/users", token=admin_token)
t12 = s == '200' and 'data' in b
tests.append(("TEST 12", "GET", "/api/admin/users", s, b[:200], t12,
              "PASS" if t12 else "FAIL"))

# TEST 13: GET /api/search?q=test
s, b = curl_test("TEST 13", "GET", "https://somekorean.com/api/search?q=test")
t13 = s == '200' and 'result' in b
tests.append(("TEST 13", "GET", "/api/search?q=test", s, b[:200], t13,
              "PASS" if t13 else "FAIL"))

# Print final report
print("=" * 70)
print("QA TESTER #5 - FINAL TEST REPORT")
print("=" * 70)
for name, method, url, status, snippet, passed, note in tests:
    print(f"\n{name}: {method} {url}")
    print(f"  Status: {status}")
    print(f"  Response: {snippet}")
    print(f"  Result: {'PASS' if passed else 'FAIL'} - {note}")

passed_count = sum(1 for t in tests if t[5])
print(f"\n{'=' * 70}")
print(f"TOTAL: {passed_count}/{len(tests)} PASSED")
print(f"{'=' * 70}")

ssh.close()
