import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# Check market condition ENUM
print("=== market_items condition column ===")
out, _ = run("mysql -u$(grep DB_USERNAME /var/www/somekorean/.env | cut -d= -f2) -p$(grep DB_PASSWORD /var/www/somekorean/.env | cut -d= -f2) $(grep DB_DATABASE /var/www/somekorean/.env | cut -d= -f2) -e \"SHOW COLUMNS FROM market_items LIKE 'condition'\" 2>/dev/null")
print(out)

# Check DB env
out, _ = run("grep 'DB_' /var/www/somekorean/.env 2>/dev/null | head -10")
print(out)

# Check market_items table columns
print("\n=== market_items ENUM values ===")
out, _ = run("grep -r 'condition' /var/www/somekorean/database/migrations/ 2>/dev/null | grep -i 'enum\\|string' | head -10")
print(out)

# Check jobs 500 error - recent logs
print("\n=== 최근 jobs POST 500 에러 ===")
out, _ = run("tail -50 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null | grep -B2 -A10 'job_post\\|JobPost' | head -60")
print(out[:2000])

# Check jobs_posts table columns
print("\n=== job_posts migration ===")
out, _ = run("find /var/www/somekorean/database/migrations -name '*job*' 2>/dev/null | xargs grep -n 'column\\|enum\\|string' 2>/dev/null | head -20")
print(out)

# Check RealEstateListing - does it have latitude/longitude?
print("\n=== RealEstate lat/lng in store method ===")
out, _ = run("grep -n 'latitude\\|longitude\\|lat\\|lng' /var/www/somekorean/app/Http/Controllers/API/RealEstateController.php 2>/dev/null | head -15")
print(out)

# Check RealEstate store - does it accept lat/lng?
print("\n=== RealEstate fillable lat check ===")
out, _ = run("grep -n 'latitude\\|longitude' /var/www/somekorean/app/Models/RealEstateListing.php 2>/dev/null | head -5")
print(out)
out, _ = run("find /var/www/somekorean/app/Models -name '*Real*' -exec grep -n 'latitude\\|longitude' {} \\; 2>/dev/null")
print(out)

client.close()
print("\n완료")
