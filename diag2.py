import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# Check latest errors
print("=== 최근 500 에러 상세 ===")
out, _ = run("tail -100 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -B1 -A15 'Server Error\\|Exception\\|Error' | head -120")
print(out[:4000])

# Check jobs store
print("\n=== JobController store 메서드 전체 ===")
out, _ = run("sed -n '30,55p' /var/www/somekorean/app/Http/Controllers/API/JobController.php")
print(out)

# Check market store
print("\n=== MarketController store 메서드 전체 ===")
out, _ = run("sed -n '30,55p' /var/www/somekorean/app/Http/Controllers/API/MarketController.php")
print(out)

# Check events category validation
print("\n=== EventController store 메서드 전체 ===")
out, _ = run("sed -n '55,100p' /var/www/somekorean/app/Http/Controllers/API/EventController.php")
print(out)

# Check event category values
print("\n=== Event model/enum category ===")
out, _ = run("grep -n 'category' /var/www/somekorean/app/Models/Event.php 2>/dev/null | head -20")
print(out)
out, _ = run("grep -rn 'category.*culture\\|category.*community\\|커뮤니티' /var/www/somekorean/app/ 2>/dev/null | head -10")
print(out)

# Check real estate lat/lng
print("\n=== RealEstateController store ===")
out, _ = run("sed -n '30,65p' /var/www/somekorean/app/Http/Controllers/API/RealEstateController.php")
print(out)

print("\n=== RealEstate model fillable ===")
out, _ = run("grep -A20 'fillable' /var/www/somekorean/app/Models/RealEstate.php 2>/dev/null || find /var/www/somekorean/app/Models -name '*Real*' -exec grep -A20 'fillable' {} \\;")
print(out)

# Check DB schema for real estate
print("\n=== RealEstate migration (lat/lng fields) ===")
out, _ = run("find /var/www/somekorean/database/migrations -name '*real*' 2>/dev/null | xargs grep -n 'lat\\|lng\\|location\\|address' 2>/dev/null | head -15")
print(out)

client.close()
print("\n완료")
