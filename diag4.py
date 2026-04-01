import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# Check the auth middleware block to see which routes are inside
print("=== Auth middleware group routes (lines 270-380) ===")
out, _ = run("sed -n '270,385p' /var/www/somekorean/routes/api.php")
print(out)

print("\n=== Is auth middleware protecting jobs PUT? Full context ===")
out, _ = run("grep -n 'auth:api\\|middleware.*auth\\|group.*function' /var/www/somekorean/routes/api.php | head -20")
print(out)

# Check if T2 is actually being rejected for own content
# The issue might be T2 is also admin or user 1 = user 2
print("\n=== Check users 1 and 2 ===")
out, _ = run("""mysql -usomekorean_user -p'SK_DB@2026!secure' somekorean -e "SELECT id, name, email, is_admin FROM users LIMIT 3" 2>/dev/null""")
print(out)

# Check JWT guard
print("\n=== JWT Auth guard config ===")
out, _ = run("grep -A5 'api' /var/www/somekorean/config/auth.php 2>/dev/null | head -20")
print(out)

# Try to decode T2 token manually - check sub
import base64, json as j
T2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NvbWVrb3JlYW4uY29tIiwiaWF0IjoxNzc0OTYyMjkwLCJleHAiOjE3NzQ5NjU4OTAsIm5iZiI6MTc3NDk2MjI5MCwianRpIjoiMGFsVDFuRmRIb1lPQnQ3QSIsInN1YiI6IjIiLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.GZxxjexQzrLa1cwfA4UZaF7VA0ENaFVf9CP_qtNr2fM"
parts = T2.split('.')
payload = parts[1]
# Add padding
payload += '=' * (4 - len(payload) % 4)
decoded = base64.b64decode(payload)
print(f"\nT2 JWT payload: {decoded.decode()}")

# Check if T2 token is expired
print("\n=== Token expiration check ===")
out, _ = run("php -r \"$t='" + T2 + "'; $p=explode('.',$t)[1]; $p=str_pad($p,strlen($p)+4-strlen($p)%4,'='); $d=json_decode(base64_decode($p)); echo 'exp: '.$d->exp.' | now: '.time().' | expired: '.($d->exp<time()?'YES':'NO');\" 2>/dev/null")
print(out)

# Regenerate fresh tokens
print("\n=== 새 토큰 생성 ===")
out, _ = run("php /tmp/tok.php 2>/dev/null")
print(out[:200])

client.close()
print("\n완료")
