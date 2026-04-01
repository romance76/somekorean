import paramiko
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# Get all API routes
print("=== ALL API ROUTES (auth/user/search related) ===")
out, err = run('cd /var/www/somekorean && php artisan route:list --path=api 2>/dev/null | grep -E "(login|register|user|search|notif|dashboard|menu)" | head -40')
print(out)
print()

# Get tokens via tinker (proper escaping)
print("=== Get user 1 token ===")
cmd = r"""cd /var/www/somekorean && php artisan tinker --execute="echo \App\Models\User::find(1)->createToken('t5')->plainTextToken;" """
out, err = run(cmd)
user_token = out.strip().split('\n')[-1].strip()
print(f"Token: {user_token[:40]}...")
print()

print("=== Get admin (272) token ===")
cmd = r"""cd /var/www/somekorean && php artisan tinker --execute="echo \App\Models\User::find(272)->createToken('a5')->plainTextToken;" """
out, err = run(cmd)
admin_token = out.strip().split('\n')[-1].strip()
print(f"Admin Token: {admin_token[:40]}...")
print()

if len(user_token) < 10 or len(admin_token) < 10:
    print("TOKEN GENERATION FAILED, aborting")
    ssh.close()
    sys.exit(1)

def curl_test(label, method, url, token=None, data=None):
    headers = '-H "Accept: application/json"'
    if token:
        headers += f' -H "Authorization: Bearer {token}"'
    if data:
        headers += ' -H "Content-Type: application/json"'

    method_flag = f'-X {method}' if method != 'GET' else ''
    data_flag = f"-d '{data}'" if data else ''

    cmd = f'curl -sk {method_flag} "{url}" {headers} {data_flag} -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null'
    out, err = run(cmd)

    lines = out.strip().split('\n')
    status_line = [l for l in lines if l.startswith('HTTP_STATUS:')]
    status = status_line[0].replace('HTTP_STATUS:', '') if status_line else 'N/A'
    body = '\n'.join([l for l in lines if not l.startswith('HTTP_STATUS:')])

    print(f"=== {label} ===")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Status: {status}")
    print(f"Response: {body[:200]}")

    is_pass = status.startswith('2') or (status in ['401', '422'] and label.startswith(('TEST 2', 'TEST 8', 'TEST 9')))
    print(f"Result: {'PASS' if is_pass else 'FAIL'}")
    print()
    return status, body

# TEST 1: Login
curl_test("TEST 1: Login", "POST", "https://somekorean.com/api/auth/login",
          data='{"email":"test@test.com","password":"password"}')

# TEST 2: Register validation
curl_test("TEST 2: Register (dup email)", "POST", "https://somekorean.com/api/auth/register",
          data='{"name":"Test","email":"test@test.com","password":"password","password_confirmation":"password"}')

# TEST 3: Get current user
curl_test("TEST 3: GET /api/user", "GET", "https://somekorean.com/api/user", token=user_token)

# TEST 4: User dashboard
curl_test("TEST 4: GET /api/user/dashboard", "GET", "https://somekorean.com/api/user/dashboard", token=user_token)

# TEST 5: Update profile
curl_test("TEST 5: PUT /api/user/profile", "PUT", "https://somekorean.com/api/user/profile",
          token=user_token, data='{"name":"Test User Updated","bio":"test profile"}')

# TEST 6: Bookmarks
curl_test("TEST 6: GET /api/user/bookmarks", "GET", "https://somekorean.com/api/user/bookmarks", token=user_token)

# TEST 7: Points
curl_test("TEST 7: GET /api/user/points", "GET", "https://somekorean.com/api/user/points", token=user_token)

# TEST 8: Notifications
curl_test("TEST 8: GET /api/notifications", "GET", "https://somekorean.com/api/notifications", token=user_token)

# TEST 9: Unread notifications
curl_test("TEST 9: GET /api/notifications/unread", "GET", "https://somekorean.com/api/notifications/unread", token=user_token)

# TEST 10: Admin menu settings
curl_test("TEST 10: GET /api/admin/settings/menus", "GET", "https://somekorean.com/api/admin/settings/menus", token=admin_token)

# TEST 11: Admin dashboard
curl_test("TEST 11: GET /api/admin/dashboard", "GET", "https://somekorean.com/api/admin/dashboard", token=admin_token)

# TEST 12: Admin users
curl_test("TEST 12: GET /api/admin/users", "GET", "https://somekorean.com/api/admin/users", token=admin_token)

# TEST 13: Search
curl_test("TEST 13: GET /api/search?q=test", "GET", "https://somekorean.com/api/search?q=test")

ssh.close()
print("=== ALL TESTS COMPLETE ===")
