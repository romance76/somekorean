import paramiko
import os

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print('Connecting...')
client.connect(HOST, username=USER, password=PASS, timeout=15)
print('Connected!')

sftp = client.open_sftp()

def run(cmd, show=True, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if show:
        if out: print('OUT:', out.strip())
        if err and 'Warning' not in err: print('ERR:', err.strip()[:500])
    return out, err

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}', show=False)
    sftp.put(local_path, remote_path)
    print(f'  OK {os.path.basename(local_path)}')

files = [
    ('resources/js/pages/community/PostDetail.vue',     'resources/js/pages/community/PostDetail.vue'),
    ('resources/js/pages/community/BoardList.vue',      'resources/js/pages/community/BoardList.vue'),
    ('resources/js/pages/community/ClubDetail.vue',     'resources/js/pages/community/ClubDetail.vue'),
    ('resources/js/pages/community/ClubList.vue',       'resources/js/pages/community/ClubList.vue'),
    ('resources/js/pages/events/EventDetail.vue',       'resources/js/pages/events/EventDetail.vue'),
    ('resources/js/pages/events/EventList.vue',         'resources/js/pages/events/EventList.vue'),
    ('resources/js/pages/events/EventCreate.vue',       'resources/js/pages/events/EventCreate.vue'),
    ('resources/js/pages/jobs/JobDetail.vue',           'resources/js/pages/jobs/JobDetail.vue'),
    ('resources/js/pages/jobs/JobList.vue',             'resources/js/pages/jobs/JobList.vue'),
    ('resources/js/pages/jobs/JobWrite.vue',            'resources/js/pages/jobs/JobWrite.vue'),
    ('resources/js/pages/recipes/RecipeDetail.vue',     'resources/js/pages/recipes/RecipeDetail.vue'),
    ('resources/js/pages/recipes/RecipeList.vue',       'resources/js/pages/recipes/RecipeList.vue'),
    ('resources/js/pages/market/MarketDetail.vue',      'resources/js/pages/market/MarketDetail.vue'),
    ('resources/js/pages/market/MarketList.vue',        'resources/js/pages/market/MarketList.vue'),
    ('resources/js/pages/market/MarketWrite.vue',       'resources/js/pages/market/MarketWrite.vue'),
    ('resources/js/pages/realestate/RealEstateDetail.vue', 'resources/js/pages/realestate/RealEstateDetail.vue'),
    ('resources/js/pages/realestate/RealEstateList.vue',   'resources/js/pages/realestate/RealEstateList.vue'),
    ('resources/js/pages/realestate/RealEstateWrite.vue',  'resources/js/pages/realestate/RealEstateWrite.vue'),
]

print(f'\n=== 파일 업로드 ({len(files)}개) ===')
for local_rel, remote_rel in files:
    local_path  = os.path.join(LOCAL, local_rel)
    remote_path = f'{APP}/{remote_rel}'
    upload(local_path, remote_path)

print('\n=== npm run build ===')
out, err = run(f'cd {APP} && npm run build 2>&1', timeout=300)
if 'built in' in out or 'vite' in out.lower():
    print('\nBUILD SUCCESS!')
else:
    print('\n결과:', out[-500:] if out else err[-500:])

sftp.close()
client.close()
print('\n=== 배포 완료 ===')
