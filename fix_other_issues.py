import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    return out, err

# Check for other \$ issues in other controllers
print("=== Checking other controllers for \\$ issues ===")
out, _ = run("grep -rl '\\\\$' /var/www/somekorean/app/Http/Controllers/API/ 2>/dev/null")
print(f"Files with \\$ issues:\n{out}")

# Check MarketController for \$ issues
print("\n=== MarketController \\$ issues ===")
out, _ = run("grep -n '\\\\$' /var/www/somekorean/app/Http/Controllers/API/MarketController.php 2>/dev/null")
print(out if out else "None found")

# Check JobController
print("\n=== JobController \\$ issues ===")
out, _ = run("grep -n '\\\\$' /var/www/somekorean/app/Http/Controllers/API/JobController.php 2>/dev/null")
print(out if out else "None found")

# Check RealEstateController
print("\n=== RealEstateController \\$ issues ===")
out, _ = run("grep -n '\\\\$' /var/www/somekorean/app/Http/Controllers/API/RealEstateController.php 2>/dev/null")
print(out if out else "None found")

# Check Market 500 error - look at full store method
print("\n=== MarketController store method ===")
out, _ = run("sed -n '30,60p' /var/www/somekorean/app/Http/Controllers/API/MarketController.php")
print(out)

# Check if market has sold endpoint
print("\n=== Market sold/status endpoint ===")
out, _ = run("grep -n 'sold\\|status\\|complete\\|Route' /var/www/somekorean/app/Http/Controllers/API/MarketController.php 2>/dev/null | head -20")
print(out)

# Check routes for market
print("\n=== api.php market routes ===")
out, _ = run("grep -n 'market\\|sold' /var/www/somekorean/routes/api.php 2>/dev/null | head -20")
print(out)

# Check jobs routes
print("\n=== api.php jobs routes ===")
out, _ = run("grep -n 'jobs\\|bookmark\\|like' /var/www/somekorean/routes/api.php 2>/dev/null | head -30")
print(out)

# Check events routes
print("\n=== api.php events routes ===")
out, _ = run("grep -n 'events\\|attend\\|like\\|bookmark' /var/www/somekorean/routes/api.php 2>/dev/null | head -20")
print(out)

# Clear laravel cache
print("\n=== Clearing Laravel cache ===")
out, err = run("cd /var/www/somekorean && php artisan config:clear 2>&1 && php artisan route:clear 2>&1 && php artisan cache:clear 2>&1")
print(out)

client.close()
print("\n완료")
