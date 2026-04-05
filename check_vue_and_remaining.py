import paramiko
import json
import subprocess

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# ============================================================
# 1. Remaining FAIL: R-4 (lat/lng not in response)
# ============================================================
print("=== R-4: POST /api/realestate 응답에서 latitude 확인 ===")
# Check full response body from a real estate POST
out, _ = run("""curl -s -X POST https://somekorean.com/api/realestate \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyNzYwLCJleHAiOjE3NzQ5NjYzNjAsIm5iZiI6MTc3NDk2Mjc2MCwianRpIjoieEJoUFQwNllHbE9xVFlBWSIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.pwQUPTgynYgqgvLfw4cpf2QWykKuH5sknaGZciG1QUw" \
  -d '{"title":"Test RE","description":"Test","type":"렌트","price":2000,"address":"123 Main St","region":"NY","latitude":40.7678,"longitude":-73.8330}' 2>/dev/null""")
print(out[:500])

# Check what fields are in the response
try:
    data = json.loads(out)
    listing = data.get('listing', data)
    print(f"\nKeys in response: {list(listing.keys()) if isinstance(listing, dict) else 'not dict'}")
    print(f"latitude: {listing.get('latitude', 'NOT FOUND')}")
    print(f"longitude: {listing.get('longitude', 'NOT FOUND')}")
    # cleanup
    re_id = listing.get('id')
    if re_id:
        run(f"""curl -s -X DELETE https://somekorean.com/api/realestate/{re_id} -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyNzYwLCJleHAiOjE3NzQ5NjYzNjAsIm5iZiI6MTc3NDk2Mjc2MCwianRpIjoieEJoUFQwNllHbE9xVFlBWSIsInN1YiI6IjEiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.pwQUPTgynYgqgvLfw4cpf2QWykKuH5sknaGZciG1QUw" 2>/dev/null""")
except:
    pass

# ============================================================
# 2. Check market /sold endpoint
# ============================================================
print("\n=== M-4: PATCH /sold 엔드포인트 존재 여부 ===")
out, _ = run("grep -n 'sold' /var/www/somekorean/routes/api.php 2>/dev/null | head -10")
print(out if out else "PATCH /sold 없음")

# ============================================================
# Vue 프론트엔드 권한 체크
# ============================================================
print("\n=== JobDetail.vue 수정/삭제 버튼 권한 체크 ===")
out, _ = run("grep -n 'delete\\|edit\\|수정\\|삭제\\|user_id\\|auth\\|is_admin' /var/www/somekorean/resources/js/pages/jobs/JobDetail.vue 2>/dev/null | head -20")
print(out if out else "파일 없음")

print("\n=== JobDetail.vue 파일 존재 여부 ===")
out, _ = run("find /var/www/somekorean/resources/js -name '*Job*' -o -name '*job*' 2>/dev/null | head -10")
print(out)

print("\n=== market Vue 파일 ===")
out, _ = run("find /var/www/somekorean/resources/js -name '*Market*' -o -name '*market*' 2>/dev/null | head -10")
print(out)

print("\n=== realestate Vue 파일 ===")
out, _ = run("find /var/www/somekorean/resources/js -name '*Real*' -o -name '*Estate*' -o -name '*realestate*' 2>/dev/null | head -10")
print(out)

print("\n=== events Vue 파일 ===")
out, _ = run("find /var/www/somekorean/resources/js -name '*Event*' -o -name '*event*' 2>/dev/null | head -10")
print(out)

client.close()
print("\n완료")
