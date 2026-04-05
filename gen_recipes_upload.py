#!/usr/bin/env python3
"""Generate and upload recipe PHP scripts to the server."""
import paramiko
import json
import random
import time

def ssh_exec(ssh, cmd, timeout=300):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

def upload_file(ssh, content, remote_path):
    sftp = ssh.open_sftp()
    with sftp.file(remote_path, 'w') as f:
        f.write(content)
    sftp.close()

# Unsplash image mappings by category and type
IMAGES = {
    'soup': [
        '1547592180-85f173990554',
        '1635363638580-c2809d049eee',
        '1583224964978-2257b8a8d849',
        '1546456073-92b9f0a8d413',
    ],
    'grill': [
        '1562802378-063ec186a863',
        '1567337710282-00832b415979',
        '1590301157890-4810ed352733',
        '1598515214211-89d3c73ae83b',
    ],
    'banchan': [
        '1512621776951-a57141f2eefd',
        '1540914124281-342587941389',
        '1518977676601-b53f82aba655',
        '1464226184884-fa280b87c399',
        '1455619452474-d2be8b1e70cd',
    ],
    'american': [
        '1568901346375-23c9450c58cd',
        '1565299585323-38d6b0865b47',
        '1529042410759-befb1204b468',
        '1476224203421-9ac39bcb3327',
        '1544025162-d76694265947',
        '1504674900247-0877df9cc836',
    ],
    'fusion': [
        '1555949258-eb67b1ef0ceb',
        '1603133872878-684f208fb84b',
    ],
    'dessert': [
        '1551024506-0bccd828d307',
        '1558618666-fcd25c85cd64',
        '1481833761820-0509d3217039',
        '1544145945-f90425340c7e',
    ],
}

def img(photo_id):
    return f'https://images.unsplash.com/photo-{photo_id}?w=600&q=80'

def pick_img(category, title):
    """Pick image based on category and title keywords."""
    t = title.lower()
    if category == 1:
        # Korean main
        soup_kw = ['찌개','탕','국','수프','국밥','설렁','해장','칼국수','수제비','만두국','떡국','곰탕','사골','누룽지','죽','짬뽕']
        if any(k in t for k in soup_kw):
            return img(random.choice(IMAGES['soup']))
        return img(random.choice(IMAGES['grill']))
    elif category == 2:
        return img(random.choice(IMAGES['banchan']))
    elif category == 3:
        burger_kw = ['버거','핫도그','샌드위치']
        pasta_kw = ['파스타','스파게티','라자냐','카르보나라','알프레도']
        steak_kw = ['스테이크','립','로스트','미트로프','브리스킷']
        dessert_kw = ['파이','케이크','쿠키','브라우니','도넛','머핀','아이스크림','시나몬','컵케이크']
        if any(k in t for k in burger_kw):
            return img('1568901346375-23c9450c58cd')
        if any(k in t for k in pasta_kw):
            return img('1476224203421-9ac39bcb3327')
        if any(k in t for k in steak_kw):
            return img(random.choice(['1544025162-d76694265947','1504674900247-0877df9cc836']))
        if any(k in t for k in dessert_kw):
            return img(random.choice(IMAGES['dessert']))
        return img(random.choice(IMAGES['american']))
    elif category == 4:
        return img(random.choice(IMAGES['fusion'] + IMAGES['grill'][:1] + IMAGES['american'][:1]))
    elif category == 5:
        soup_kw = ['찌개','탕','국','수프']
        if any(k in t for k in soup_kw):
            return img(random.choice(IMAGES['soup']))
        banchan_kw = ['나물','조림','볶음','무침','김치']
        if any(k in t for k in banchan_kw):
            return img(random.choice(IMAGES['banchan']))
        return img(random.choice(IMAGES['grill']))
    elif category == 6:
        drink_kw = ['차','라떼','커피','아메리카노','에이드','스무디','주스','밀크','아인슈페너','수정과','식혜']
        if any(k in t for k in drink_kw):
            return img(random.choice(['1481833761820-0509d3217039','1544145945-f90425340c7e']))
        bread_kw = ['빵','크로와상','스콘','식빵','모닝빵','토스트']
        if any(k in t for k in bread_kw):
            return img('1558618666-fcd25c85cd64')
        return img(random.choice(IMAGES['dessert']))
    return img(random.choice(IMAGES['grill']))

# ============ RECIPE DATA ============

CAT1_RECIPES = [
    "김치찌개", "된장찌개", "순두부찌개", "부대찌개", "삼겹살구이", "불고기", "갈비탕", "삼계탕",
    "닭볶음탕", "곱창볶음", "낙지볶음", "제육볶음", "떡볶이", "비빔밥", "냉면", "설렁탕",
    "해장국", "국밥", "칼국수", "쌀국수", "감자탕", "추어탕", "김치볶음밥", "오삼불고기",
    "닭갈비", "해물탕", "매운탕", "콩나물국밥", "순대국", "육개장", "닭한마리", "보쌈",
    "족발", "쭈꾸미볶음", "양념치킨", "프라이드치킨", "닭강정", "만두국", "떡국", "미역국",
    "소머리국밥", "갈비찜", "아구찜", "해물찜", "대구탕", "김치전", "해물파전", "감자전",
    "빈대떡", "녹두전", "부추전", "고기만두", "김치만두", "물만두", "찐만두", "수제비",
    "잔치국수", "비빔국수", "밀면", "쫄면", "잡채", "어묵탕", "떡만두국", "꼬리곰탕",
    "사골국", "도가니탕", "누룽지탕", "전복죽", "소고기무국", "콩비지찌개", "청국장",
    "동태찌개", "알탕", "대하구이", "조기구이", "고등어구이", "삼치구이", "장어구이",
    "갈치조림", "고등어조림", "보리밥", "돌솥비빔밥", "회덮밥", "낙지덮밥", "카레라이스",
    "오므라이스", "볶음우동", "짜장면", "짬뽕", "탕수육", "잔치비빔밥", "산채비빔밥",
    "참치김밥", "소고기김밥", "치즈김밥", "충무김밥", "누드김밥", "삼각김밥", "주먹밥",
    "유부초밥", "매운갈비찜", "소갈비구이", "양곱창구이", "닭곰탕", "들깨수제비",
]

CAT2_RECIPES = [
    "시금치나물", "콩나물무침", "감자조림", "두부조림", "멸치볶음", "무생채", "계란말이",
    "간장계란조림", "깍두기", "오이소박이", "배추김치", "열무김치", "파김치", "깻잎장아찌",
    "마늘장아찌", "고추장아찌", "진미채볶음", "어묵볶음", "미역줄기볶음", "느타리버섯볶음",
    "새송이버섯구이", "연근조림", "우엉조림", "장조림", "메추리알조림", "콩자반",
    "무말랭이무침", "도라지나물", "고사리나물", "취나물", "호박볶음", "가지볶음", "오이무침",
    "파프리카볶음", "브로콜리볶음", "양배추볶음", "깻잎전", "김치전", "동그랑땡", "두부부침",
    "야채전", "호박전", "고추튀김", "김무침", "마늘종볶음", "고추장멸치", "간장멸치",
    "견과류멸치", "잔멸치볶음", "젓갈", "양념장", "쌈장", "초장", "겉절이", "나박김치",
    "동치미", "총각김치", "부추무침", "미나리무침", "냉이무침", "달래무침", "상추겉절이",
    "잡채", "골뱅이무침", "꽃게무침", "새우장", "간장게장", "양념게장", "명란젓",
    "오징어젓", "꽁치무조림", "두부김치", "떡갈비", "불고기전", "김말이", "춘권", "순대",
    "오뎅볶음", "떡꼬치", "치즈스틱", "고구마맛탕", "감자채볶음", "연근칩", "채소튀김",
    "깻잎김치", "고수나물", "숙주나물", "미나리나물", "참나물", "콩나물밥", "김치볶음",
    "멸치주먹밥", "주먹밥", "유부주머니", "두부강정", "오징어채볶음", "쥐포구이",
    "북어채볶음", "황태채볶음", "비름나물", "애호박볶음", "버섯잡채", "들깨무나물",
]

CAT3_RECIPES = [
    "클래식 버거", "치즈버거", "BBQ 풀드포크", "스테이크", "립아이 스테이크", "뉴욕 스트립",
    "맥앤치즈", "그릴드치즈 샌드위치", "BLT 샌드위치", "클럽 샌드위치", "필리 치즈스테이크",
    "치킨윙", "버팔로윙", "BBQ 갈비", "프라이드 치킨", "미트로프", "포트로스트",
    "칠리 콘 카르네", "클램차우더", "치킨누들수프", "시저 샐러드", "콥 샐러드", "핫도그",
    "시카고 딥디쉬 피자", "뉴욕 스타일 피자", "라자냐", "스파게티 미트볼", "알프레도 파스타",
    "카르보나라", "쉬림프 스캠피", "피쉬 앤 칩스", "피시타코", "크랩케이크", "로브스터 롤",
    "케이준 새우", "잠발라야", "검보", "하와이안 포키", "슬로피조", "미트볼 서브", "타코",
    "부리토", "나초", "치킨 케사디아", "치킨 파히타", "터키 샌드위치", "루벤 샌드위치",
    "프렌치 딥", "스테이크 샐러드", "웨지 샐러드", "코울슬로", "베이크드 포테이토",
    "매쉬드 포테이토", "프렌치프라이", "양파링", "콘브레드", "비스킷 앤 그레이비",
    "팬케이크", "프렌치 토스트", "에그 베네딕트", "옴렛", "스크램블 에그", "해시브라운",
    "바나나 브레드", "초코칩 쿠키", "브라우니", "애플파이", "펌킨파이", "치즈케이크",
    "아이스크림 선데이", "시나몬롤", "도넛", "머핀", "컵케이크", "카우보이 스테이크",
    "텍사스 BBQ 브리스킷", "캐롤라이나 풀드포크", "내슈빌 핫치킨", "캘리포니아 피쉬타코",
    "루이지애나 검보", "보스턴 클램차우더", "뉴욕 치즈케이크", "하와이안 라이스볼",
    "치킨 프라이드 스테이크", "치킨 팟파이", "셰퍼드 파이", "터키 미트로프",
    "칠리 치즈 독", "로드 나초", "퀘소 딥", "과카몰레", "살사", "코른 샐러드",
    "BBQ 치킨 피자", "버팔로 치킨 딥", "프렌치 어니언 수프", "토마토 수프",
    "치킨 앤 와플", "비스킷", "캐서롤", "포테이토 스킨", "치킨 텐더", "어니언링",
]

CAT4_RECIPES = [
    "고추장 파스타", "김치 버거", "불고기 타코", "된장 아보카도 토스트", "김치 프라이드 라이스",
    "떡볶이 리조또", "갈릭버터 새우덮밥", "고추장 핫윙", "김치 치즈 그릴드 샌드위치",
    "불고기 피자", "김치 퀘사디아", "고추장 치킨 샌드위치", "비빔밥 볼", "김치 맥앤치즈",
    "떡 프렌치 토스트", "소불고기 치즈스테이크", "매운 참치 포키", "김치 프렌치프라이",
    "고추장 하니 윙", "된장 페스토 파스타", "김치 그릴드 치즈", "불고기 나초",
    "매운 떡꼬치 핫도그", "김치찌개 스튜", "소불고기 래핑", "치즈 떡볶이", "크림 라볶이",
    "매운 치킨 버거", "간장 버터 스테이크", "고추장 BBQ 립", "김치 볶음밥 오므라이스",
    "된장 크림 파스타", "참깨 누들", "비빔 콜드 누들", "매운 해물 파스타", "고추장 슬라이더",
    "불고기 김밥 롤", "매운 새우 타코", "김치 핫도그", "고추장 마요 버거", "된장 치킨 샐러드",
    "불고기 볶음 누들", "깻잎 페스토 파스타", "김치 팬케이크", "고추장 프라이드 치킨",
    "매운 갈비 타코", "된장 그레이비 비스킷", "김치 카르보나라", "불고기 슬라이더",
    "고추장 살몬", "김치전 피자", "된장 리조또", "매운 오징어 파스타", "김치 부리토",
    "불고기 랩", "고추장 미트볼", "된장 수프", "매운 치킨 래핑", "김치 스프링롤",
    "참치 비빔 보울", "소불고기 덮밥", "고추장 에그 베네딕트", "김치 오믈렛", "불고기 볶음밥",
    "된장 드레싱 샐러드", "매운 두부 타코", "김치 치즈 프라이", "고추장 바비큐 치킨",
    "된장 마리네 스테이크", "매운 참치 멜트", "김치 크로크무슈", "불고기 칼조네",
    "고추장 글레이즈 연어", "된장 버터 옥수수", "매운 에비 템푸라", "김치 리조또",
    "고추장 칠리", "된장 크림 수프", "불고기 파니니", "매운 낙지 파스타", "김치 와플",
    "고추장 포크촙", "된장 버거", "매운 크랩케이크", "김치 퐁듀", "불고기 스테이크 볶음밥",
    "고추장 연어 보울", "된장 치킨 윙", "매운 참치 포켓", "김치 라자냐", "고추장 미소 수프",
    "된장 감바스", "불고기 스프링롤", "매운 닭가슴살 랩", "김치 도리아", "고추장 하쉬",
    "된장 포테이토 수프", "매운 치킨 도리아", "불고기 토스트", "김치 크림 파스타",
    "고추장 치킨 보울", "된장 새우 파스타", "불고기 스테이크 샐러드", "김치 치킨 랩",
]

CAT5_RECIPES = [
    "Costco 삼겹살 수육", "H-Mart 미역국", "Walmart 두부 순두부찌개", "Target 케일 된장국",
    "Trader Joe's 고추장 샐러드", "Costco 소불고기 덮밥", "Kroger 닭 삼계탕",
    "Target 시금치 나물", "Walmart 감자 감자조림", "Costco 새우 새우볶음밥",
    "H-Mart 고등어 구이", "Costco 대하 소금구이", "Walmart 닭가슴살 닭갈비",
    "Target 브로콜리 나물", "Kroger 소고기 불고기", "Costco 연어 연어구이",
    "Trader Joe's 두부 마파두부", "Walmart 돼지고기 제육볶음", "Target 양배추 겉절이",
    "Costco 갈비 LA갈비구이", "H-Mart 김치 김치찌개", "Kroger 닭 닭볶음탕",
    "Walmart 계란 계란말이", "Target 파프리카 잡채", "Costco 소시지 부대찌개",
    "Trader Joe's 콩나물 콩나물국", "Walmart 감자 감자탕", "Kroger 소고기 육개장",
    "Target 시금치 된장국", "Costco 치킨 양념치킨", "H-Mart 오징어 오징어볶음",
    "Walmart 두부 두부조림", "Target 당근 잡채", "Costco 삼겹살 삼겹살구이",
    "Kroger 돼지고기 보쌈", "Trader Joe's 버섯 버섯전골", "Walmart 닭 닭강정",
    "Target 고구마 고구마조림", "Costco 새우 새우전", "H-Mart 낙지 낙지볶음",
    "Kroger 소고기 소고기무국", "Walmart 배추 배추김치", "Target 무 깍두기",
    "Costco 연어 연어덮밥", "Trader Joe's 아보카도 비빔밥", "Walmart 닭 삼계탕",
    "Target 케일 나물무침", "Costco 돼지고기 떡갈비", "Kroger 계란 간장계란조림",
    "H-Mart 멸치 멸치볶음", "Walmart 두부 순두부찌개", "Target 브로콜리 된장무침",
    "Costco 소고기 갈비찜", "Trader Joe's 콩 콩나물무침", "Walmart 닭 프라이드치킨",
    "Target 양파 양파볶음", "Costco 새우 감바스", "Kroger 돼지고기 김치볶음밥",
    "H-Mart 고등어 고등어조림", "Walmart 계란 계란찜", "Target 감자 감자채볶음",
    "Costco 치킨 닭한마리", "Trader Joe's 두부 두부부침", "Walmart 소고기 잡채",
    "Target 호박 호박전", "Costco 삼겹살 삼겹살김치찜", "Kroger 닭 닭꼬치",
    "H-Mart 오징어 오징어무침", "Walmart 배추 배추된장국", "Target 시금치 시금치나물",
    "Costco 연어 연어스테이크", "Trader Joe's 두부 마파두부덮밥", "Walmart 돼지고기 돈카츠",
    "Target 양배추 양배추볶음", "Costco 소고기 소고기장조림", "Kroger 계란 에그드롭수프",
    "H-Mart 새우 새우볶음", "Walmart 닭 닭가슴살 샐러드", "Target 당근 당근조림",
    "Costco 돼지고기 족발", "Trader Joe's 버섯 버섯볶음", "Walmart 두부 두부스테이크",
    "Target 고구마 고구마튀김", "Costco 새우 크림새우", "Kroger 소고기 미역국",
    "H-Mart 낙지 낙지덮밥", "Walmart 배추 김치전", "Target 무 무나물",
    "Costco 연어 연어김밥", "Trader Joe's 아보카도 아보카도김밥", "Walmart 닭 닭죽",
    "Target 케일 케일전", "Costco 소고기 소고기김밥", "Kroger 돼지고기 돼지불백",
    "H-Mart 멸치 멸치국수", "Walmart 두부 두부김치", "Target 브로콜리 브로콜리무침",
    "Costco 삼겹살 대패삼겹살볶음", "Trader Joe's 콩 콩비지찌개",
    "Walmart 닭 닭갈비볶음밥", "Target 양파 양파링튀김",
    "Costco 새우 새우튀김", "Kroger 소고기 소고기덮밥",
]

CAT6_RECIPES = [
    "호떡", "약과", "수정과", "식혜", "붕어빵", "인절미", "송편", "찹쌀떡", "경단", "유과",
    "한과", "다식", "강정", "매작과", "꿀타래", "호두과자", "팥빙수", "아이스크림 떡",
    "떡꼬치", "핫떡", "씨앗호떡", "계란빵", "달고나", "슈크림", "미니 크로플", "와플",
    "도넛", "마카롱", "티라미수", "크렘 브릴레", "판나코타", "무스케이크", "치즈케이크",
    "생크림케이크", "초코케이크", "당근케이크", "바나나빵", "쿠키", "브라우니", "스콘",
    "머핀", "크로와상", "식빵", "모닝빵", "소보로빵", "단팥빵", "크림빵", "야채빵",
    "피자빵", "소시지빵", "유자차", "대추차", "쌍화차", "생강차", "매실차", "녹차라떼",
    "고구마라떼", "밀크티", "아인슈페너", "카페라떼", "아메리카노", "스무디", "에이드",
    "밀크쉐이크", "과일주스", "떡카페", "약밥", "찰떡쿠키", "떡케이크", "한라봉 케이크",
    "고구마 케이크", "딸기 케이크", "녹차 케이크", "흑임자 라떼", "미숫가루",
    "팥죽", "호박죽", "타피오카 밀크티", "망고 스무디", "딸기 에이드", "복숭아 에이드",
    "레몬 에이드", "유자 에이드", "자몽 에이드", "블루베리 스무디", "바나나 스무디",
    "초콜릿 머핀", "블루베리 머핀", "레몬 스콘", "치즈 스콘", "시나몬 롤", "꽈배기",
    "찹쌀 도넛", "크림치즈 빵", "마늘빵", "멜론빵", "카스테라", "바움쿠헨", "롤케이크",
    "에클레어", "슈크림빵", "타르트", "과일타르트", "에그타르트",
]

ALL_CATS = {
    1: CAT1_RECIPES,
    2: CAT2_RECIPES,
    3: CAT3_RECIPES,
    4: CAT4_RECIPES,
    5: CAT5_RECIPES,
    6: CAT6_RECIPES,
}

# Ingredient templates per category
def gen_ingredients(cat, title):
    """Generate ingredients based on category and title."""
    t = title.lower()
    base_ingredients = {
        1: [
            [{"name":"김치","amount":"200g"},{"name":"돼지고기","amount":"150g"},{"name":"두부","amount":"1모"},{"name":"대파","amount":"1대"},{"name":"고춧가루","amount":"1큰술"},{"name":"다진마늘","amount":"1큰술"}],
            [{"name":"소고기","amount":"200g"},{"name":"양파","amount":"1개"},{"name":"간장","amount":"3큰술"},{"name":"설탕","amount":"1큰술"},{"name":"참기름","amount":"1큰술"},{"name":"후추","amount":"약간"}],
            [{"name":"닭고기","amount":"1마리"},{"name":"대파","amount":"2대"},{"name":"마늘","amount":"5쪽"},{"name":"생강","amount":"1톨"},{"name":"소금","amount":"적당량"},{"name":"후추","amount":"약간"}],
            [{"name":"돼지고기","amount":"300g"},{"name":"고추장","amount":"2큰술"},{"name":"고춧가루","amount":"1큰술"},{"name":"간장","amount":"2큰술"},{"name":"설탕","amount":"1큰술"},{"name":"양파","amount":"1개"},{"name":"대파","amount":"1대"}],
            [{"name":"밥","amount":"2공기"},{"name":"계란","amount":"2개"},{"name":"당근","amount":"1/2개"},{"name":"시금치","amount":"한줌"},{"name":"참기름","amount":"1큰술"},{"name":"고추장","amount":"1큰술"}],
        ],
        2: [
            [{"name":"시금치","amount":"200g"},{"name":"소금","amount":"약간"},{"name":"다진마늘","amount":"1큰술"},{"name":"참기름","amount":"1큰술"},{"name":"깨소금","amount":"1큰술"}],
            [{"name":"감자","amount":"3개"},{"name":"간장","amount":"3큰술"},{"name":"설탕","amount":"1큰술"},{"name":"물엿","amount":"1큰술"},{"name":"다진마늘","amount":"1큰술"}],
            [{"name":"두부","amount":"1모"},{"name":"간장","amount":"2큰술"},{"name":"고춧가루","amount":"1큰술"},{"name":"대파","amount":"1대"},{"name":"참기름","amount":"1큰술"}],
            [{"name":"멸치","amount":"100g"},{"name":"간장","amount":"1큰술"},{"name":"설탕","amount":"1큰술"},{"name":"물엿","amount":"1큰술"},{"name":"깨소금","amount":"약간"}],
            [{"name":"콩나물","amount":"200g"},{"name":"소금","amount":"약간"},{"name":"다진마늘","amount":"1큰술"},{"name":"참기름","amount":"1큰술"},{"name":"고춧가루","amount":"1큰술"}],
        ],
        3: [
            [{"name":"소고기 패티","amount":"200g"},{"name":"번","amount":"2개"},{"name":"양상추","amount":"2장"},{"name":"토마토","amount":"1개"},{"name":"치즈","amount":"2장"},{"name":"케첩","amount":"적당량"}],
            [{"name":"파스타면","amount":"200g"},{"name":"크림소스","amount":"200ml"},{"name":"베이컨","amount":"100g"},{"name":"파마산치즈","amount":"30g"},{"name":"올리브오일","amount":"2큰술"},{"name":"소금","amount":"약간"}],
            [{"name":"닭날개","amount":"1kg"},{"name":"버팔로소스","amount":"100ml"},{"name":"버터","amount":"30g"},{"name":"마늘","amount":"3쪽"},{"name":"소금","amount":"약간"},{"name":"후추","amount":"약간"}],
            [{"name":"스테이크","amount":"300g"},{"name":"올리브오일","amount":"2큰술"},{"name":"버터","amount":"30g"},{"name":"마늘","amount":"3쪽"},{"name":"소금","amount":"적당량"},{"name":"후추","amount":"적당량"},{"name":"로즈마리","amount":"2줄기"}],
            [{"name":"또띠아","amount":"4장"},{"name":"소고기","amount":"200g"},{"name":"양상추","amount":"적당량"},{"name":"토마토","amount":"1개"},{"name":"사워크림","amount":"50g"},{"name":"살사소스","amount":"적당량"}],
        ],
        4: [
            [{"name":"파스타면","amount":"200g"},{"name":"고추장","amount":"2큰술"},{"name":"올리브오일","amount":"2큰술"},{"name":"마늘","amount":"3쪽"},{"name":"파마산치즈","amount":"30g"},{"name":"대파","amount":"1대"}],
            [{"name":"불고기","amount":"200g"},{"name":"또띠아","amount":"4장"},{"name":"양상추","amount":"적당량"},{"name":"고추장마요","amount":"2큰술"},{"name":"깻잎","amount":"5장"}],
            [{"name":"김치","amount":"200g"},{"name":"치즈","amount":"100g"},{"name":"식빵","amount":"4장"},{"name":"버터","amount":"30g"},{"name":"마요네즈","amount":"1큰술"}],
            [{"name":"떡","amount":"200g"},{"name":"크림소스","amount":"200ml"},{"name":"모짜렐라","amount":"100g"},{"name":"양파","amount":"1/2개"},{"name":"마늘","amount":"2쪽"},{"name":"파마산","amount":"적당량"}],
            [{"name":"소불고기","amount":"200g"},{"name":"밥","amount":"2공기"},{"name":"계란","amount":"2개"},{"name":"김치","amount":"100g"},{"name":"참기름","amount":"1큰술"},{"name":"깨소금","amount":"약간"}],
        ],
        5: [
            [{"name":"Costco 삼겹살","amount":"500g"},{"name":"대파","amount":"2대"},{"name":"마늘","amount":"5쪽"},{"name":"된장","amount":"2큰술"},{"name":"소금","amount":"약간"}],
            [{"name":"Walmart 닭가슴살","amount":"300g"},{"name":"양파","amount":"1개"},{"name":"간장","amount":"3큰술"},{"name":"고추장","amount":"2큰술"},{"name":"고춧가루","amount":"1큰술"},{"name":"대파","amount":"1대"}],
            [{"name":"Costco 연어","amount":"300g"},{"name":"소금","amount":"약간"},{"name":"후추","amount":"약간"},{"name":"레몬","amount":"1개"},{"name":"올리브오일","amount":"2큰술"}],
            [{"name":"Target 두부","amount":"1모"},{"name":"김치","amount":"200g"},{"name":"돼지고기","amount":"100g"},{"name":"대파","amount":"1대"},{"name":"고춧가루","amount":"1큰술"},{"name":"다진마늘","amount":"1큰술"}],
            [{"name":"Kroger 소고기","amount":"200g"},{"name":"무","amount":"1/2개"},{"name":"대파","amount":"1대"},{"name":"다진마늘","amount":"1큰술"},{"name":"국간장","amount":"2큰술"},{"name":"소금","amount":"약간"}],
        ],
        6: [
            [{"name":"찹쌀가루","amount":"200g"},{"name":"설탕","amount":"50g"},{"name":"소금","amount":"약간"},{"name":"식용유","amount":"적당량"},{"name":"꿀","amount":"2큰술"}],
            [{"name":"밀가루","amount":"200g"},{"name":"버터","amount":"100g"},{"name":"설탕","amount":"80g"},{"name":"계란","amount":"2개"},{"name":"베이킹파우더","amount":"1작은술"}],
            [{"name":"녹차가루","amount":"2큰술"},{"name":"우유","amount":"300ml"},{"name":"설탕","amount":"2큰술"},{"name":"얼음","amount":"적당량"}],
            [{"name":"크림치즈","amount":"200g"},{"name":"설탕","amount":"80g"},{"name":"계란","amount":"2개"},{"name":"생크림","amount":"100ml"},{"name":"바닐라","amount":"1작은술"},{"name":"비스킷","amount":"100g"}],
            [{"name":"팥","amount":"300g"},{"name":"설탕","amount":"100g"},{"name":"소금","amount":"약간"},{"name":"찹쌀가루","amount":"200g"},{"name":"물","amount":"적당량"}],
        ],
    }
    return random.choice(base_ingredients[cat])

def gen_steps(cat, title):
    """Generate steps based on category."""
    steps_pool = {
        1: [
            [{"step":1,"description":"재료를 깨끗이 씻고 먹기 좋은 크기로 썰어줍니다."},{"step":2,"description":"냄비에 참기름을 두르고 고기를 먼저 볶아줍니다."},{"step":3,"description":"양념 재료를 넣고 물을 부어 끓여줍니다."},{"step":4,"description":"중불에서 20분간 끓인 후 대파를 넣고 마무리합니다."}],
            [{"step":1,"description":"고기를 양념에 30분 이상 재워둡니다."},{"step":2,"description":"팬을 강불로 달군 후 고기를 올려 구워줍니다."},{"step":3,"description":"앞뒤로 골고루 구워 접시에 담아냅니다."},{"step":4,"description":"상추와 쌈장을 곁들여 완성합니다."}],
            [{"step":1,"description":"모든 재료를 준비하고 손질합니다."},{"step":2,"description":"밥을 그릇에 담고 재료를 올려줍니다."},{"step":3,"description":"양념장을 끼얹고 잘 비벼 먹습니다."}],
            [{"step":1,"description":"재료를 손질하고 양념을 만들어둡니다."},{"step":2,"description":"끓는 물에 면을 삶아 찬물에 헹궈줍니다."},{"step":3,"description":"그릇에 면을 담고 육수를 부어줍니다."},{"step":4,"description":"고명을 올려 완성합니다."}],
            [{"step":1,"description":"반죽 재료를 섞어 반죽을 만듭니다."},{"step":2,"description":"팬에 기름을 두르고 반죽을 올려 부쳐줍니다."},{"step":3,"description":"앞뒤로 노릇하게 구워 완성합니다."}],
        ],
        2: [
            [{"step":1,"description":"채소를 깨끗이 씻어 손질합니다."},{"step":2,"description":"끓는 물에 데쳐 찬물에 헹궈 물기를 짜줍니다."},{"step":3,"description":"양념 재료를 넣고 골고루 무쳐줍니다."}],
            [{"step":1,"description":"재료를 먹기 좋은 크기로 썰어줍니다."},{"step":2,"description":"냄비에 양념과 재료를 넣고 중불에서 조려줍니다."},{"step":3,"description":"양념이 고루 배면 불을 끄고 그릇에 담습니다."}],
            [{"step":1,"description":"재료를 준비하고 양념장을 만듭니다."},{"step":2,"description":"팬에 기름을 두르고 재료를 볶아줍니다."},{"step":3,"description":"양념을 넣고 중불에서 볶아 완성합니다."}],
        ],
        3: [
            [{"step":1,"description":"Prepare all ingredients and season as needed."},{"step":2,"description":"Heat the pan or grill to medium-high heat."},{"step":3,"description":"Cook the main ingredient until done."},{"step":4,"description":"Assemble and serve with your favorite sides."}],
            [{"step":1,"description":"재료를 준비하고 양념합니다."},{"step":2,"description":"오븐을 180도로 예열합니다."},{"step":3,"description":"재료를 오븐에 넣고 정해진 시간만큼 구워줍니다."},{"step":4,"description":"완성된 요리를 접시에 담아 서빙합니다."}],
            [{"step":1,"description":"모든 재료를 준비합니다."},{"step":2,"description":"큰 냄비에 물을 끓이고 재료를 넣습니다."},{"step":3,"description":"중불에서 30분간 끓여줍니다."},{"step":4,"description":"간을 맞추고 그릇에 담아냅니다."}],
        ],
        4: [
            [{"step":1,"description":"한국식 양념 재료를 먼저 준비합니다."},{"step":2,"description":"서양식 베이스를 만들어줍니다."},{"step":3,"description":"한국 양념을 서양 요리에 접목시켜 조리합니다."},{"step":4,"description":"플레이팅하여 완성합니다."}],
            [{"step":1,"description":"퓨전 소스 재료를 섞어 준비합니다."},{"step":2,"description":"메인 재료를 손질하고 조리합니다."},{"step":3,"description":"소스를 곁들여 접시에 담아냅니다."}],
        ],
        5: [
            [{"step":1,"description":"마트에서 구매한 재료를 손질합니다."},{"step":2,"description":"한국식 양념을 준비합니다."},{"step":3,"description":"미국 재료에 한국 양념을 적용하여 조리합니다."},{"step":4,"description":"완성된 요리를 그릇에 담아냅니다."}],
            [{"step":1,"description":"재료를 깨끗이 씻고 준비합니다."},{"step":2,"description":"냄비나 팬을 준비하고 조리를 시작합니다."},{"step":3,"description":"양념을 넣고 적절히 익혀줍니다."},{"step":4,"description":"맛을 보고 간을 조절하여 완성합니다."}],
        ],
        6: [
            [{"step":1,"description":"반죽 재료를 섞어 반죽을 만듭니다."},{"step":2,"description":"반죽을 적당한 크기로 빚어줍니다."},{"step":3,"description":"기름에 튀기거나 오븐에 구워줍니다."},{"step":4,"description":"완성된 간식을 접시에 담아냅니다."}],
            [{"step":1,"description":"재료를 계량하여 준비합니다."},{"step":2,"description":"재료를 섞어 베이스를 만듭니다."},{"step":3,"description":"냉장고에서 차갑게 굳혀 완성합니다."}],
            [{"step":1,"description":"물을 끓이고 재료를 넣어줍니다."},{"step":2,"description":"약불에서 우려내며 향을 냅니다."},{"step":3,"description":"체에 걸러 잔에 담아냅니다."}],
        ],
    }
    return random.choice(steps_pool[cat])

def gen_tips(cat, title):
    tips_pool = [
        [{"tip":"재료는 신선한 것을 사용하면 맛이 훨씬 좋아요."}],
        [{"tip":"불 조절이 핵심이에요. 센 불에서 빠르게 조리하세요."}],
        [{"tip":"양념을 미리 만들어두면 조리 시간을 줄일 수 있어요."}],
        [{"tip":"냉장고에서 하루 숙성시키면 더 깊은 맛이 나요."}],
        [{"tip":"기호에 따라 매운 정도를 조절하세요."}],
        [{"tip":"남은 것은 밀폐용기에 담아 냉동보관하면 오래 먹을 수 있어요."}],
        [{"tip":"고기는 결 반대 방향으로 썰면 더 부드러워요."}],
        [{"tip":"마지막에 참기름을 넣으면 풍미가 올라가요."}],
    ]
    return random.choice(tips_pool)

def gen_tags(cat, title):
    t = title
    base_tags = {
        1: ["한식","메인요리","집밥","한국요리"],
        2: ["반찬","한식반찬","집밥","밑반찬"],
        3: ["미국음식","양식","서양요리"],
        4: ["퓨전","한미퓨전","퓨전요리","크리에이티브"],
        5: ["미국재료","한식","마트요리","쉬운한식"],
        6: ["간식","디저트","달콤한","간편"],
    }
    tags = base_tags[cat][:2]
    # Add title-based tags
    kw_map = {"김치":["김치","발효식품"], "버거":["버거","패스트푸드"], "파스타":["파스타","면요리"],
              "떡":["떡","전통간식"], "차":["음료","차"], "빵":["빵","베이커리"],
              "찌개":["찌개","국물요리"], "구이":["구이","그릴"], "볶음":["볶음","빠른요리"],
              "나물":["나물","건강식"], "조림":["조림","밑반찬"], "샐러드":["샐러드","건강식"]}
    for k, v in kw_map.items():
        if k in t:
            tags.extend(v[:1])
            break
    return list(set(tags))[:4]

def gen_intro(cat, title):
    intros = {
        1: [
            f"정성 가득한 {title}, 온 가족이 좋아하는 든든한 한 끼입니다.",
            f"집에서 쉽게 만드는 {title}! 누구나 성공할 수 있는 레시피예요.",
            f"깊고 진한 맛의 {title}, 한국인의 소울푸드입니다.",
            f"어머니의 손맛을 담은 정통 {title} 레시피를 소개합니다.",
            f"간단하면서도 맛있는 {title}, 바쁜 날에도 뚝딱 만들 수 있어요.",
        ],
        2: [
            f"밥도둑 {title}! 매일 먹어도 질리지 않는 반찬입니다.",
            f"냉장고에 항상 있으면 좋은 {title}, 만들어두면 든든해요.",
            f"간단하게 만드는 {title}, 초보 요리사도 쉽게 따라할 수 있어요.",
            f"엄마의 손맛을 담은 {title}, 어디서도 못 먹는 집밥 반찬!",
            f"건강하고 맛있는 {title}, 매일 식탁에 올려보세요.",
        ],
        3: [
            f"본격 미국식 {title}! 집에서 레스토랑 맛을 즐겨보세요.",
            f"미국 현지 맛 그대로! 정통 {title} 레시피입니다.",
            f"주말 브런치로 딱 좋은 {title}, 가족 모두 좋아해요.",
            f"파티 음식으로 최고인 {title}, 손님 초대 시 강력 추천!",
        ],
        4: [
            f"한국과 미국의 맛이 만난 {title}! 새로운 맛의 발견입니다.",
            f"퓨전 요리의 정수, {title}! 독특하면서도 맛있어요.",
            f"한식 양념과 서양 요리의 환상 조합, {title}을 소개합니다.",
            f"익숙하면서도 새로운 {title}, 색다른 맛을 원할 때 추천!",
        ],
        5: [
            f"미국 마트 재료로 만드는 정통 한식! {title} 레시피입니다.",
            f"한국 식재료 없이도 OK! 미국 마트 재료로 만드는 {title}.",
            f"가까운 마트에서 쉽게 구할 수 있는 재료로 만드는 {title}!",
            f"미국 생활 필수 레시피! 현지 재료로 만드는 {title}.",
        ],
        6: [
            f"달콤한 {title}, 간식으로 딱 좋아요!",
            f"집에서 만드는 {title}, 카페 부럽지 않은 맛이에요.",
            f"아이들이 좋아하는 {title}! 간단하게 만들어보세요.",
            f"티타임에 즐기는 {title}, 하루의 피로를 달래줘요.",
        ],
    }
    return random.choice(intros[cat])

def gen_difficulty():
    return random.choices(['easy','medium','hard'], weights=[40,45,15])[0]

def gen_cook_time():
    times = ['10분','15분','20분','25분','30분','40분','50분','1시간','1시간 30분','2시간']
    return random.choice(times)

def gen_calories():
    return random.randint(100, 800)

def gen_servings():
    return random.choice([1,2,2,2,3,4,4])

# Generate all recipes
def generate_all_recipes():
    recipes = []
    for cat_id, titles in ALL_CATS.items():
        for title in titles:
            recipe = {
                'category_id': cat_id,
                'title': title,
                'intro': gen_intro(cat_id, title),
                'difficulty': gen_difficulty(),
                'cook_time': gen_cook_time(),
                'calories': gen_calories(),
                'servings': gen_servings(),
                'ingredients': gen_ingredients(cat_id, title),
                'steps': gen_steps(cat_id, title),
                'tips': gen_tips(cat_id, title),
                'tags': gen_tags(cat_id, title),
                'image_url': pick_img(cat_id, title),
            }
            recipes.append(recipe)
    return recipes

def build_php_script(recipes, admin_id=2):
    """Build PHP script for batch insert."""
    php = """<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('memory_limit', '512M');
set_time_limit(600);

$pdo = new PDO('mysql:host=localhost;dbname=somekorean;charset=utf8mb4', 'somekorean_user', 'SK_DB@2026!secure');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$admin_id = """ + str(admin_id) + """;

// Check admin exists
$stmt = $pdo->query("SELECT id FROM users WHERE is_admin=1 LIMIT 1");
$row = $stmt->fetch();
if ($row) $admin_id = $row['id'];

$inserted = 0;
$skipped = 0;
$errors = 0;

// Get existing titles
$existing = [];
$stmt = $pdo->query("SELECT title FROM recipe_posts");
while ($row = $stmt->fetch()) {
    $existing[$row['title']] = true;
}

$recipes = json_decode(file_get_contents('/var/www/somekorean/recipe_data.json'), true);

$stmt = $pdo->prepare("INSERT INTO recipe_posts (category_id, user_id, title, intro, difficulty, cook_time, calories, servings, ingredients, steps, tips, tags, image_url, image_credit, source, created_at, updated_at, is_hidden, view_count, like_count, bookmark_count) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,?,0,0)");

foreach ($recipes as $r) {
    if (isset($existing[$r['title']])) {
        $skipped++;
        continue;
    }

    // Random date in last 6 months
    $days_ago = rand(0, 180);
    $hours = rand(0, 23);
    $mins = rand(0, 59);
    $created = date('Y-m-d H:i:s', strtotime("-{$days_ago} days -{$hours} hours -{$mins} minutes"));
    $updated = $created;
    $view_count = rand(10, 500);

    try {
        $stmt->execute([
            $r['category_id'],
            $admin_id,
            $r['title'],
            $r['intro'],
            $r['difficulty'],
            $r['cook_time'],
            $r['calories'],
            $r['servings'],
            json_encode($r['ingredients'], JSON_UNESCAPED_UNICODE),
            json_encode($r['steps'], JSON_UNESCAPED_UNICODE),
            json_encode($r['tips'], JSON_UNESCAPED_UNICODE),
            json_encode($r['tags'], JSON_UNESCAPED_UNICODE),
            $r['image_url'],
            'Unsplash',
            'system',
            $created,
            $updated,
            $view_count,
        ]);
        $inserted++;
        $existing[$r['title']] = true;
    } catch (Exception $e) {
        $errors++;
        echo "Error: " . $r['title'] . " - " . $e->getMessage() . "\\n";
    }
}

echo "\\n=== Recipe Generation Complete ===\\n";
echo "Inserted: $inserted\\n";
echo "Skipped (duplicate): $skipped\\n";
echo "Errors: $errors\\n";

// Show counts per category
$stmt = $pdo->query("SELECT category_id, COUNT(*) as cnt FROM recipe_posts GROUP BY category_id ORDER BY category_id");
echo "\\nRecipes per category:\\n";
while ($row = $stmt->fetch()) {
    echo "  Category {$row['category_id']}: {$row['cnt']}\\n";
}
$stmt = $pdo->query("SELECT COUNT(*) as total FROM recipe_posts");
$row = $stmt->fetch();
echo "Total recipes: {$row['total']}\\n";
"""
    return php

def build_likes_comments_php():
    return """<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('memory_limit', '512M');
set_time_limit(600);

$pdo = new PDO('mysql:host=localhost;dbname=somekorean;charset=utf8mb4', 'somekorean_user', 'SK_DB@2026!secure');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Get all user IDs
$users = [];
$stmt = $pdo->query("SELECT id FROM users");
while ($row = $stmt->fetch()) {
    $users[] = $row['id'];
}
$user_count = count($users);
echo "Found $user_count users\\n";

if ($user_count < 2) {
    echo "Not enough users for likes/comments\\n";
    exit;
}

// Get all recipe IDs
$recipes = [];
$stmt = $pdo->query("SELECT id, created_at FROM recipe_posts ORDER BY id");
while ($row = $stmt->fetch()) {
    $recipes[] = $row;
}
echo "Found " . count($recipes) . " recipes\\n";

$comments_list = [
    "진짜 맛있었어요! 가족들이 너무 좋아했어요 👍",
    "생각보다 어렵지 않네요. 초보도 할 수 있어요!",
    "재료 손질이 좀 걸리지만 결과물은 최고예요",
    "팁 대로 했더니 훨씬 맛있었어요. 감사합니다!",
    "다음엔 치즈 올려서 해볼게요 ㅎㅎ",
    "우리 아이가 엄청 잘 먹었어요. 강추!",
    "양념 비율이 딱 맞네요. 레스토랑 맛 나요",
    "냉장고에 있는 재료로 대충 했는데도 맛있어요",
    "이거 처음 해봤는데 성공했어요!! 너무 행복 ㅠㅠ",
    "간이 좀 강한 편이에요. 간장 조금 줄이는 게 나을 것 같아요",
    "사진보다 실제로 훨씬 맛있어요!",
    "만들기 쉽고 맛있어서 자주 해먹을 것 같아요",
    "재료 구하기가 좀 어렵네요. 대체 재료 알려주실 분?",
    "완전 성공! 남편이 맛있다고 또 만들어달래요 ❤️",
    "처음엔 실패했는데 두 번째엔 완벽했어요",
    "불 조절이 중요한 것 같아요. 약불로 천천히 하세요",
    "한 번에 두 배로 만들어서 냉동해뒀어요!",
    "저는 고춧가루 좀 더 넣었는데 더 맛있었어요 🌶️"
];

$total_likes = 0;
$total_comments = 0;

// For each recipe, generate likes and comments
$like_stmt = $pdo->prepare("INSERT IGNORE INTO recipe_likes (recipe_id, user_id, created_at) VALUES (?, ?, ?)");
$comment_stmt = $pdo->prepare("INSERT INTO recipe_comments (recipe_id, user_id, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)");

foreach ($recipes as $recipe) {
    $recipe_id = $recipe['id'];
    $base_time = strtotime($recipe['created_at']);

    // Random likes: 5-47
    $like_count = rand(5, 47);
    $like_users = array_rand(array_flip($users), min($like_count, $user_count));
    if (!is_array($like_users)) $like_users = [$like_users];

    foreach ($like_users as $uid) {
        $like_time = date('Y-m-d H:i:s', $base_time + rand(3600, 86400 * 30));
        try {
            $like_stmt->execute([$recipe_id, $uid, $like_time]);
            $total_likes++;
        } catch (Exception $e) {
            // duplicate, skip
        }
    }

    // Random comments: 2-11
    $comment_count = rand(2, 11);
    for ($i = 0; $i < $comment_count; $i++) {
        $uid = $users[array_rand($users)];
        $content = $comments_list[array_rand($comments_list)];
        $comment_time = date('Y-m-d H:i:s', $base_time + rand(3600, 86400 * 60));
        try {
            $comment_stmt->execute([$recipe_id, $uid, $content, $comment_time, $comment_time]);
            $total_comments++;
        } catch (Exception $e) {
            echo "Comment error: " . $e->getMessage() . "\\n";
        }
    }
}

echo "\\nGenerated $total_likes likes and $total_comments comments\\n";

// Update like_count on recipe_posts
$pdo->exec("UPDATE recipe_posts r SET like_count = (SELECT COUNT(*) FROM recipe_likes WHERE recipe_id = r.id)");
echo "Updated like_count on recipe_posts\\n";

// Final stats
echo "\\n=== Final Statistics ===\\n";
$stmt = $pdo->query("SELECT category_id, COUNT(*) as cnt FROM recipe_posts GROUP BY category_id ORDER BY category_id");
$cat_names = [1=>'한식 메인', 2=>'한식 반찬', 3=>'미국 음식', 4=>'한미 퓨전', 5=>'미국재료로 한식', 6=>'간식/디저트'];
echo "\\nCategory breakdown:\\n";
while ($row = $stmt->fetch()) {
    $name = $cat_names[$row['category_id']] ?? 'Unknown';
    echo "  {$name} (cat {$row['category_id']}): {$row['cnt']} recipes\\n";
}

$stmt = $pdo->query("SELECT COUNT(*) as total FROM recipe_posts");
$row = $stmt->fetch();
echo "\\nTotal recipes: {$row['total']}\\n";

$stmt = $pdo->query("SELECT COUNT(*) as total FROM recipe_likes");
$row = $stmt->fetch();
echo "Total likes: {$row['total']}\\n";

$stmt = $pdo->query("SELECT COUNT(*) as total FROM recipe_comments");
$row = $stmt->fetch();
echo "Total comments: {$row['total']}\\n";

$stmt = $pdo->query("SELECT AVG(like_count) as avg_likes FROM recipe_posts");
$row = $stmt->fetch();
echo "Average likes per recipe: " . round($row['avg_likes'], 1) . "\\n";

$stmt = $pdo->query("SELECT COUNT(*) / (SELECT COUNT(*) FROM recipe_posts) as avg_comments FROM recipe_comments");
$row = $stmt->fetch();
echo "Average comments per recipe: " . round($row['avg_comments'], 1) . "\\n";
"""

def main():
    print("Generating recipe data...")
    recipes = generate_all_recipes()
    print(f"Generated {len(recipes)} recipes")

    # Count per category
    from collections import Counter
    cat_counts = Counter(r['category_id'] for r in recipes)
    for cat_id in sorted(cat_counts):
        print(f"  Category {cat_id}: {cat_counts[cat_id]} recipes")

    # Connect
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

    # Upload recipe data as JSON
    import json
    recipe_json = json.dumps(recipes, ensure_ascii=False)
    print(f"Recipe data JSON size: {len(recipe_json)} bytes")
    upload_file(ssh, recipe_json, '/var/www/somekorean/recipe_data.json')
    print("Uploaded recipe_data.json")

    # Upload PHP scripts
    php_script = build_php_script(recipes)
    upload_file(ssh, php_script, '/var/www/somekorean/gen_recipes.php')
    print("Uploaded gen_recipes.php")

    likes_script = build_likes_comments_php()
    upload_file(ssh, likes_script, '/var/www/somekorean/gen_likes_comments.php')
    print("Uploaded gen_likes_comments.php")

    # Execute recipe generation
    print("\n--- Running gen_recipes.php ---")
    out, err = ssh_exec(ssh, "cd /var/www/somekorean && php gen_recipes.php")
    print(out)
    if err and 'Warning' not in err:
        print("STDERR:", err)

    # Execute likes/comments generation
    print("\n--- Running gen_likes_comments.php ---")
    out, err = ssh_exec(ssh, "cd /var/www/somekorean && php gen_likes_comments.php")
    print(out)
    if err and 'Warning' not in err:
        print("STDERR:", err)

    # Cleanup
    print("\nCleaning up temporary files...")
    ssh_exec(ssh, "rm -f /var/www/somekorean/recipe_data.json /var/www/somekorean/gen_recipes.php /var/www/somekorean/gen_likes_comments.php")

    ssh.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
