import paramiko, sys, json, random
from datetime import datetime, timedelta

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

events = [
    {"title":"애틀랜타 한인 골프 토너먼트","desc":"한인 골프 동호회 주최 봄 토너먼트. 초보부터 상급자까지 참여 가능합니다.","loc":"Atlanta, GA","cat":"sports","max":80,"price":"50.00"},
    {"title":"LA 한식 축제 2026","desc":"LA 한인타운에서 열리는 대규모 한식 축제. 떡볶이, 김밥, 비빔밥 등 다양한 한식을 즐기세요.","loc":"Los Angeles, CA","cat":"food","max":500,"price":"0.00"},
    {"title":"K-POP 댄스 워크숍","desc":"BTS, BLACKPINK 안무를 배울 수 있는 K-POP 댄스 클래스입니다.","loc":"New York, NY","cat":"culture","max":40,"price":"25.00"},
    {"title":"한인 비즈니스 네트워킹","desc":"미국 내 한인 사업가, 전문직 종사자들의 네트워킹 행사입니다.","loc":"Chicago, IL","cat":"business","max":100,"price":"15.00"},
    {"title":"SAT 준비 무료 세미나","desc":"대입 준비를 위한 SAT 전략 세미나. 한인 학부모와 학생 대상.","loc":"Atlanta, GA","cat":"education","max":60,"price":"0.00"},
    {"title":"한인 엄마 모임","desc":"미국에서 아이를 키우는 한인 엄마들의 정기 모임입니다.","loc":"Dallas, TX","cat":"meetup","max":30,"price":"0.00"},
    {"title":"한국 영화의 밤","desc":"최신 한국 영화 상영회. 팝콘과 한국 간식이 제공됩니다.","loc":"Seattle, WA","cat":"culture","max":80,"price":"10.00"},
    {"title":"한인 축구 리그","desc":"매주 토요일 오전 한인 축구 리그입니다. 실력 무관 누구나 참여 가능.","loc":"Houston, TX","cat":"sports","max":40,"price":"0.00"},
    {"title":"한국어 교실 (초급)","desc":"한국어를 배우고 싶은 한인 2세, 3세를 위한 초급 한국어 수업입니다.","loc":"San Francisco, CA","cat":"education","max":20,"price":"0.00"},
    {"title":"한인 교회 부활절 행사","desc":"한인 교회에서 진행하는 부활절 특별 예배와 에그 헌트 행사입니다.","loc":"Atlanta, GA","cat":"general","max":200,"price":"0.00"},
    {"title":"김치 담그기 체험","desc":"전통 방식의 김치 담그기를 배울 수 있는 체험 행사입니다.","loc":"Los Angeles, CA","cat":"food","max":25,"price":"20.00"},
    {"title":"한인 시니어 건강 체조","desc":"65세 이상 시니어를 위한 건강 체조 프로그램입니다.","loc":"New York, NY","cat":"meetup","max":40,"price":"0.00"},
    {"title":"한인 스타트업 세미나","desc":"실리콘밸리에서 활동하는 한인 창업가들의 경험 공유 세미나.","loc":"San Francisco, CA","cat":"business","max":60,"price":"10.00"},
    {"title":"배드민턴 동호회 대회","desc":"한인 배드민턴 동호회 연례 대회. 개인전과 복식 진행.","loc":"Chicago, IL","cat":"sports","max":32,"price":"5.00"},
    {"title":"미국 이민법 세미나","desc":"이민 변호사가 진행하는 최신 이민법 변경사항 설명회.","loc":"Dallas, TX","cat":"education","max":80,"price":"0.00"},
    {"title":"한인 봉사 바자회","desc":"지역 한인 커뮤니티 봉사 바자회. 수익금은 장학금으로 사용됩니다.","loc":"Atlanta, GA","cat":"general","max":300,"price":"0.00"},
    {"title":"한복 체험 & 사진 촬영","desc":"전통 한복을 입고 전문 사진 촬영을 할 수 있는 문화 체험 행사.","loc":"Los Angeles, CA","cat":"culture","max":50,"price":"15.00"},
    {"title":"한인 부동산 투자 설명회","desc":"미국 부동산 시장 트렌드와 한인 투자자를 위한 전략 설명회.","loc":"New York, NY","cat":"business","max":100,"price":"0.00"},
    {"title":"떡 만들기 클래스","desc":"송편, 인절미 등 전통 떡 만들기를 배울 수 있는 요리 클래스.","loc":"Seattle, WA","cat":"food","max":20,"price":"30.00"},
    {"title":"한인 볼링 대회","desc":"가족 단위 참여 가능한 한인 볼링 대회. 푸짐한 경품 준비!","loc":"Houston, TX","cat":"sports","max":60,"price":"15.00"},
    {"title":"한인 와인 모임","desc":"한인 와인 애호가들의 월례 모임. 와인 시음과 담소.","loc":"San Francisco, CA","cat":"meetup","max":25,"price":"25.00"},
    {"title":"대학 입시 설명회","desc":"아이비리그 출신 한인 멘토들의 대학 입시 전략 설명회.","loc":"Atlanta, GA","cat":"education","max":100,"price":"0.00"},
    {"title":"사물놀이 공연","desc":"한국 전통 사물놀이 공연. 북, 장구, 꽹과리의 신나는 합주.","loc":"Chicago, IL","cat":"culture","max":150,"price":"10.00"},
    {"title":"한인 마라톤 대회","desc":"한인 커뮤니티 건강 달리기 대회. 5K, 10K 코스 선택 가능.","loc":"Dallas, TX","cat":"sports","max":200,"price":"20.00"},
    {"title":"한식 바베큐 파티","desc":"주말 한식 바베큐 파티. 삼겹살, 갈비, 불고기를 구워 먹어요!","loc":"Los Angeles, CA","cat":"food","max":80,"price":"15.00"},
    {"title":"청년 네트워킹 모임","desc":"20-30대 한인 청년들의 네트워킹 모임. 진로, 취업 고민 공유.","loc":"New York, NY","cat":"meetup","max":40,"price":"0.00"},
    {"title":"한인 테니스 동호회","desc":"한인 테니스 동호회 정기 모임. 레벨별 매치 진행.","loc":"Seattle, WA","cat":"sports","max":24,"price":"5.00"},
    {"title":"한인 여성 리더십 포럼","desc":"미국 내 한인 여성 리더들의 경험을 공유하는 포럼입니다.","loc":"Houston, TX","cat":"business","max":80,"price":"10.00"},
    {"title":"서예 교실","desc":"한국 전통 서예를 배울 수 있는 문화 체험 교실입니다.","loc":"San Francisco, CA","cat":"culture","max":15,"price":"20.00"},
    {"title":"한인 헌혈 캠페인","desc":"적십자사와 함께하는 한인 커뮤니티 헌혈 캠페인.","loc":"Atlanta, GA","cat":"general","max":100,"price":"0.00"},
]

now = datetime.now()
created = 0
for i, ev in enumerate(events):
    days = random.randint(1, 90)
    hour = random.randint(9, 20)
    event_date = (now + timedelta(days=days)).replace(hour=hour, minute=0, second=0)
    date_str = event_date.strftime('%Y-%m-%d %H:%M:%S')
    user_id = random.randint(1, 137)
    attendees = random.randint(0, int(ev['max'] * 0.5))

    title = ev['title'].replace("'", "\\'")
    desc = ev['desc'].replace("'", "\\'")
    loc = ev['loc'].replace("'", "\\'")

    php = f"App\\\\Models\\\\Event::create(['user_id'=>{user_id},'title'=>'{title}','description'=>'{desc}','location'=>'{loc}','region'=>'{loc.split(',')[0].strip()}','category'=>'{ev['cat']}','max_attendees'=>{ev['max']},'attendee_count'=>{attendees},'price'=>'{ev['price']}','event_date'=>'{date_str}','status'=>'published']); echo 'ok';"

    stdin, stdout, stderr = client.exec_command(f"cd /var/www/somekorean && php artisan tinker --execute=\"{php}\"", timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if 'ok' in out:
        created += 1
    else:
        err = stderr.read().decode('utf-8', errors='replace').strip()
        sys.stdout.buffer.write(f'FAIL #{i}: {out[:100]} {err[:100]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

sys.stdout.buffer.write(f'Created {created}/{len(events)} events\n'.encode('utf-8'))

# Get total count
stdin, stdout, stderr = client.exec_command("cd /var/www/somekorean && php artisan tinker --execute=\"echo App\\\\Models\\\\Event::count();\"", timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
sys.stdout.buffer.write(f'Total events in DB: {out}\n'.encode('utf-8'))
sys.stdout.buffer.flush()
client.close()
