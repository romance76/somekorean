import paramiko, os, sys

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def log(msg):
    sys.stdout.buffer.write((msg + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    log(f'>>> {cmd[:120]}')
    if out.strip(): log(out.strip()[:1000])
    if err.strip(): log('ERR: ' + err.strip()[:500])
    return out

def upload(rel):
    local_path = os.path.join(LOCAL, *rel.split('/'))
    remote_path = f'{APP}/{rel}'
    sftp.put(local_path, remote_path)
    log(f'  UP: {rel.split("/")[-1]}')

log('=== 1. Controllers ===')
upload('app/Http/Controllers/API/JobController.php')
upload('app/Http/Controllers/API/MarketController.php')
upload('app/Http/Controllers/API/EventController.php')
upload('app/Http/Controllers/API/NewsController.php')
upload('app/Http/Controllers/API/CommentController.php')
upload('app/Http/Controllers/API/AdminSettingsController.php')

log('=== 2. Models ===')
upload('app/Models/Comment.php')

log('=== 3. Routes ===')
upload('routes/api.php')

log('=== 4. Migrations ===')
upload('database/migrations/2026_03_29_000020_create_content_likes_table.php')
upload('database/migrations/2026_03_29_000021_update_comments_polymorphic.php')

log('=== 5. Frontend ===')
upload('resources/js/stores/site.js')
upload('resources/js/app.js')
upload('resources/js/components/NavBar.vue')
upload('resources/js/pages/news/NewsList.vue')
upload('resources/js/pages/news/NewsDetail.vue')

log('=== 6. php artisan migrate ===')
run(f'cd {APP} && php artisan migrate --force 2>&1', timeout=60)

log('=== 7. Cache clear ===')
run(f'cd {APP} && php artisan config:clear && php artisan route:clear && php artisan cache:clear')

log('=== 8. npm build ===')
run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=300)

log('=== 9. Check site ===')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
log('DONE')
