import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

sftp = client.open_sftp()

def read_file(path):
    with sftp.open(path, 'r') as f:
        return f.read().decode('utf-8', errors='replace')

def write_file(path, content):
    with sftp.open(path, 'w') as f:
        f.write(content)

def check_syntax(path):
    out, err = run(f"php -l {path} 2>&1")
    return out.strip()

# ============================================================
# 1. JobController - update/destroy에 권한 체크 추가
# ============================================================
print("=== JobController update/destroy 분석 ===")
out, _ = run("sed -n '70,130p' /var/www/somekorean/app/Http/Controllers/API/JobController.php")
print(out)

print("\n=== JobController 전체 구조 ===")
out, _ = run("grep -n 'function ' /var/www/somekorean/app/Http/Controllers/API/JobController.php")
print(out)

# ============================================================
# 2. MarketController - update/destroy 권한 체크
# ============================================================
print("\n=== MarketController update/destroy ===")
out, _ = run("sed -n '75,105p' /var/www/somekorean/app/Http/Controllers/API/MarketController.php")
print(out)

print("\n=== MarketController 구조 ===")
out, _ = run("grep -n 'function ' /var/www/somekorean/app/Http/Controllers/API/MarketController.php")
print(out)

# ============================================================
# 3. RealEstateController - update/destroy 권한 체크
# ============================================================
print("\n=== RealEstateController update/destroy ===")
out, _ = run("grep -n 'function ' /var/www/somekorean/app/Http/Controllers/API/RealEstateController.php")
print(out)
out, _ = run("sed -n '60,100p' /var/www/somekorean/app/Http/Controllers/API/RealEstateController.php")
print(out)

# ============================================================
# 4. EventController - update/destroy (already fixed syntax, check logic)
# ============================================================
print("\n=== EventController update/destroy ===")
out, _ = run("grep -n 'function\|user_id\|Auth::id\|is_admin\|403' /var/www/somekorean/app/Http/Controllers/API/EventController.php | head -20")
print(out)

# Check if the issue is a missing auth check (route not using auth middleware?)
print("\n=== api.php auth middleware for update/delete routes ===")
out, _ = run("grep -n 'auth\\|middleware\\|group' /var/www/somekorean/routes/api.php | head -30")
print(out)

# Check the actual jobs update route
out, _ = run("grep -n -B2 -A5 'Route::put.*jobs\\|Route::patch.*jobs' /var/www/somekorean/routes/api.php 2>/dev/null | head -20")
print("\njobs PUT routes:")
print(out)

# Check market update/delete routes
out, _ = run("grep -n -A2 'market.*update\\|market.*destroy\\|market.*put\\|market.*delete' /var/www/somekorean/routes/api.php 2>/dev/null | head -20")
print("\nmarket update/delete routes:")
print(out)

sftp.close()
client.close()
print("\n분석 완료")
