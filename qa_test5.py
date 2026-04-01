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

results = []

# Test 1: Login
print("=== TEST 1: POST /api/login ===")
out, err = run("""curl -sk -X POST https://somekorean.com/api/login -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"password"}' -w '\\nHTTP_STATUS:%{http_code}' 2>/dev/null""")
print(out[:500])
print()

# Test 2: Register validation
print("=== TEST 2: POST /api/register (duplicate email) ===")
out, err = run("""curl -sk -X POST https://somekorean.com/api/register -H "Content-Type: application/json" -d '{"name":"Test","email":"test@test.com","password":"password","password_confirmation":"password"}' -w '\\nHTTP_STATUS:%{http_code}' 2>/dev/null""")
print(out[:500])
print()

# Test 3: Get token for user 1
print("=== TEST 3: Get token (user 1) ===")
out, err = run('cd /var/www/somekorean && php artisan tinker --execute="\\$user = App\\Models\\User::find(1); \\$token = \\$user->createToken(\'test5\')->plainTextToken; echo \\$token;"')
user_token = out.strip().split('\n')[-1].strip()
print(f"Token: {user_token[:30]}...")
print()

# Test 3b: Get user with token
print("=== TEST 3b: GET /api/user ===")
out, err = run(f'curl -sk https://somekorean.com/api/user -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 4: User dashboard
print("=== TEST 4: GET /api/user/dashboard ===")
out, err = run(f'curl -sk https://somekorean.com/api/user/dashboard -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 5: Update profile
print("=== TEST 5: PUT /api/user/profile ===")
out, err = run(f"""curl -sk -X PUT https://somekorean.com/api/user/profile -H "Authorization: Bearer {user_token}" -H "Content-Type: application/json" -d '{{"name":"Test User Updated","bio":"테스트 프로필"}}' -w '\\nHTTP_STATUS:%{{http_code}}' 2>/dev/null""")
print(out[:500])
print()

# Test 6: Bookmarks
print("=== TEST 6: GET /api/user/bookmarks ===")
out, err = run(f'curl -sk https://somekorean.com/api/user/bookmarks -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 7: Points
print("=== TEST 7: GET /api/user/points ===")
out, err = run(f'curl -sk https://somekorean.com/api/user/points -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 8: Notifications
print("=== TEST 8: GET /api/notifications ===")
out, err = run(f'curl -sk https://somekorean.com/api/notifications -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 9: Unread notifications
print("=== TEST 9: GET /api/notifications/unread ===")
out, err = run(f'curl -sk https://somekorean.com/api/notifications/unread -H "Authorization: Bearer {user_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Get admin token (user 272)
print("=== Getting admin token (user 272) ===")
out, err = run('cd /var/www/somekorean && php artisan tinker --execute="\\$user = App\\Models\\User::find(272); \\$token = \\$user->createToken(\'admin-test5\')->plainTextToken; echo \\$token;"')
admin_token = out.strip().split('\n')[-1].strip()
print(f"Admin Token: {admin_token[:30]}...")
print()

# Test 10: Admin menu settings
print("=== TEST 10: GET /api/admin/settings/menus ===")
out, err = run(f'curl -sk https://somekorean.com/api/admin/settings/menus -H "Authorization: Bearer {admin_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 11: Admin dashboard
print("=== TEST 11: GET /api/admin/dashboard ===")
out, err = run(f'curl -sk https://somekorean.com/api/admin/dashboard -H "Authorization: Bearer {admin_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 12: Admin users
print("=== TEST 12: GET /api/admin/users ===")
out, err = run(f'curl -sk https://somekorean.com/api/admin/users -H "Authorization: Bearer {admin_token}" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

# Test 13: Search
print("=== TEST 13: GET /api/search?q=test ===")
out, err = run(f'curl -sk "https://somekorean.com/api/search?q=test" -w "\\nHTTP_STATUS:%{{http_code}}" 2>/dev/null')
print(out[:500])
print()

ssh.close()
print("=== ALL TESTS COMPLETE ===")
