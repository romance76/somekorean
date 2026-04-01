#!/usr/bin/env python3
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out or err or 'NOT FOUND'

checks = [
    ('Q&A Vue 페이지', 'ls /var/www/somekorean/resources/js/pages/qa/ 2>/dev/null'),
    ('레시피 Vue 페이지', 'ls /var/www/somekorean/resources/js/pages/recipes/ 2>/dev/null'),
    ('AdminQa.vue', 'ls /var/www/somekorean/resources/js/pages/admin/AdminQa.vue 2>/dev/null'),
    ('AdminRecipes.vue', 'ls /var/www/somekorean/resources/js/pages/admin/AdminRecipes.vue 2>/dev/null'),
    ('QaController', 'ls /var/www/somekorean/app/Http/Controllers/API/QaController.php 2>/dev/null'),
    ('RecipeController', 'ls /var/www/somekorean/app/Http/Controllers/API/RecipeController.php 2>/dev/null'),
    ('AdminQaController', 'ls /var/www/somekorean/app/Http/Controllers/API/AdminQaController.php 2>/dev/null'),
    ('AdminRecipeController', 'ls /var/www/somekorean/app/Http/Controllers/API/AdminRecipeController.php 2>/dev/null'),
    ('api.php qa routes', 'grep -c "qa/" /var/www/somekorean/routes/api.php 2>/dev/null'),
    ('api.php recipe routes', 'grep -c "recipes" /var/www/somekorean/routes/api.php 2>/dev/null'),
    ('Vite build', 'ls /var/www/somekorean/public/build/manifest.json 2>/dev/null'),
    ('DB qa_posts count', 'mysql -u somekorean_user -pEhdRh0817wodl somekorean -e "SELECT COUNT(*) FROM qa_posts;" 2>/dev/null | tail -1'),
    ('DB recipe_posts count', 'mysql -u somekorean_user -pEhdRh0817wodl somekorean -e "SELECT COUNT(*) FROM recipe_posts;" 2>/dev/null | tail -1'),
]

for name, cmd in checks:
    result = ssh(cmd)
    print(f"[{name}]: {result}")

c.close()
