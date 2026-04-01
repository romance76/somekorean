import paramiko, sys, random
from datetime import datetime, timedelta

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

# Get valid user IDs first
stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"echo implode(',', App\\\\Models\\\\User::pluck('id')->toArray());\"", timeout=15)
user_ids = [int(x) for x in stdout.read().decode().strip().split(',') if x.strip().isdigit()]
sys.stdout.buffer.write(f'Valid users: {len(user_ids)}\n'.encode('utf-8')); sys.stdout.buffer.flush()

extra = [
    {"title":"코딩 부트캠프 (한인 대상)","desc":"파이썬과 웹 개발을 배우는 8주 코딩 부트캠프.","loc":"Online","cat":"education","max":30,"price":"0.00"},
    {"title":"한인 요가 클래스","desc":"한인 요가 강사와 함께하는 주 2회 요가 클래스.","loc":"Atlanta, GA","cat":"sports","max":20,"price":"10.00"},
    {"title":"한국 디저트 클래스","desc":"호떡, 붕어빵, 약과 등 한국 디저트를 만들어봐요.","loc":"Dallas, TX","cat":"food","max":15,"price":"25.00"},
    {"title":"한인 독서 모임","desc":"매월 한국 소설 1권을 읽고 토론하는 독서 모임입니다.","loc":"Seattle, WA","cat":"meetup","max":15,"price":"0.00"},
    {"title":"K-드라마 팬 미팅","desc":"K-드라마 팬들이 모여 최신 드라마를 이야기하는 모임.","loc":"Chicago, IL","cat":"culture","max":40,"price":"0.00"},
    {"title":"한인 탁구 대회","desc":"한인 탁구 동호회 연례 대회. 남녀노소 참여 가능.","loc":"Houston, TX","cat":"sports","max":32,"price":"5.00"},
    {"title":"한인 세금 신고 도움","desc":"무료 세금 신고 도움 서비스. CPA 자원봉사자가 도와드립니다.","loc":"Los Angeles, CA","cat":"general","max":50,"price":"0.00"},
    {"title":"한인 전자상거래 세미나","desc":"아마존, 쇼피파이에서 사업하는 방법을 알려드리는 세미나.","loc":"New York, NY","cat":"business","max":60,"price":"0.00"},
    {"title":"한인 사진 동호회 출사","desc":"봄꽃 출사 모임. DSLR, 스마트폰 모두 환영합니다.","loc":"San Francisco, CA","cat":"meetup","max":20,"price":"0.00"},
    {"title":"한식 상차림 클래스","desc":"한식 상차림과 예절을 배우는 문화 교실입니다.","loc":"Atlanta, GA","cat":"food","max":20,"price":"15.00"},
    {"title":"한인 미술 전시회","desc":"미국 내 한인 작가들의 현대미술 전시회입니다.","loc":"New York, NY","cat":"culture","max":100,"price":"5.00"},
]

now = datetime.now()
created = 0
for ev in extra:
    days = random.randint(1, 90)
    event_date = (now + timedelta(days=days)).replace(hour=random.randint(9,20), minute=0, second=0)
    date_str = event_date.strftime('%Y-%m-%d %H:%M:%S')
    uid = random.choice(user_ids)
    att = random.randint(0, int(ev['max'] * 0.5))
    t = ev['title'].replace("'", "\\'")
    d = ev['desc'].replace("'", "\\'")
    l = ev['loc'].replace("'", "\\'")
    r = l.split(',')[0].strip()
    php = f"App\\\\Models\\\\Event::create(['user_id'=>{uid},'title'=>'{t}','description'=>'{d}','location'=>'{l}','region'=>'{r}','category'=>'{ev['cat']}','max_attendees'=>{ev['max']},'attendee_count'=>{att},'price'=>'{ev['price']}','event_date'=>'{date_str}','status'=>'published']); echo 'ok';"
    stdin, stdout, stderr = client.exec_command(f"cd /var/www/somekorean && php artisan tinker --execute=\"{php}\"", timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if 'ok' in out: created += 1

stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"echo App\\\\Models\\\\Event::count();\"", timeout=15)
total = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'Added {created}/{len(extra)} more. Total events: {total}\n'.encode('utf-8'))
sys.stdout.buffer.flush()
client.close()
