import paramiko, base64

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# Fetch QaController.php
qa_out, _ = ssh("cat /var/www/somekorean/app/Http/Controllers/API/QaController.php")
with open("QaController.php", "w", encoding="utf-8") as f:
    f.write(qa_out)
print("QaController.php fetched, lines:", len(qa_out.splitlines()))

# Fetch RecipeController.php
recipe_out, _ = ssh("cat /var/www/somekorean/app/Http/Controllers/API/RecipeController.php")
with open("RecipeController.php", "w", encoding="utf-8") as f:
    f.write(recipe_out)
print("RecipeController.php fetched, lines:", len(recipe_out.splitlines()))

c.close()
print("Done")
