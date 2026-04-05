import paramiko, base64

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# Upload QaController.php
with open("QaController.php", "r", encoding="utf-8") as f:
    qa_content = f.read()

qa_enc = base64.b64encode(qa_content.encode('utf-8')).decode('ascii')
# Write in chunks if needed
ssh(f"echo '{qa_enc}' | base64 -d > /var/www/somekorean/app/Http/Controllers/API/QaController.php")
result, _ = ssh("wc -l /var/www/somekorean/app/Http/Controllers/API/QaController.php")
print("QaController.php uploaded, lines:", result)

# Verify the changes
result, _ = ssh("grep -n 'nickname' /var/www/somekorean/app/Http/Controllers/API/QaController.php")
print("QaController nickname references:", result)

# Upload RecipeController.php
with open("RecipeController.php", "r", encoding="utf-8") as f:
    recipe_content = f.read()

recipe_enc = base64.b64encode(recipe_content.encode('utf-8')).decode('ascii')
ssh(f"echo '{recipe_enc}' | base64 -d > /var/www/somekorean/app/Http/Controllers/API/RecipeController.php")
result, _ = ssh("wc -l /var/www/somekorean/app/Http/Controllers/API/RecipeController.php")
print("RecipeController.php uploaded, lines:", result)

# Verify the changes
result, _ = ssh("grep -n 'nickname\\|related\\|avg_rating\\|comment_count' /var/www/somekorean/app/Http/Controllers/API/RecipeController.php")
print("RecipeController references:", result)

# Clear cache
print("\nClearing cache...")
out, err = ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear", timeout=60)
print("config:clear:", out)
if err:
    print("errors:", err)

# Test endpoints
print("\nTesting recipe endpoint...")
out, err = ssh('curl -sk https://somekorean.com/api/recipes/1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(\'related:\', len(d.get(\'related\',[])), \'avg_rating:\', d.get(\'avg_rating\'), \'comment_count:\', d.get(\'comment_count\'))"', timeout=30)
print("Recipe test:", out)
if err:
    print("Recipe test err:", err)

print("\nTesting QA endpoint...")
out, err = ssh('curl -sk https://somekorean.com/api/qa/1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(\'user:\', d.get(\'user\',{}).get(\'nickname\'), d.get(\'user\',{}).get(\'username\'))"', timeout=30)
print("QA test:", out)
if err:
    print("QA test err:", err)

c.close()
print("\nAll done!")
