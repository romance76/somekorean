import pymysql, random, datetime

conn = pymysql.connect(host="127.0.0.1", user="somekorean_user", password="SK_DB@2026!secure", db="somekorean", charset="utf8mb4", autocommit=True)
cur = conn.cursor()
USER_IDS = list(range(53, 103)) + list(range(104, 188))

def rand_user(): return random.choice(USER_IDS)
def rand_date(m=6):
    now = datetime.datetime.now()
    return (now - datetime.timedelta(days=random.randint(1,m*30), hours=random.randint(0,23))).strftime("%Y-%m-%d %H:%M:%S")
def esc(s): return conn.escape_string(s)

cur.execute("SELECT id, name FROM clubs WHERE id <= 10")
clubs = cur.fetchall()

club_posts = {
    1: [
        ("이번 주 토요일 Griffith Park 테니스 모임!", "안녕하세요! 토요일 오전 9시 Griffith Park 코트에서 만나요.\n준비물: 라켓, 물, 운동화\n참가비: $5\n초보자 환영!"),
        ("테니스 라켓 추천해주세요", "중급자인데 Wilson, Head, Babolat 중 뭐가 좋을까요? 예산 $150-200"),
        ("지난 주 모임 후기!", "날씨 좋고 재밌었어요! 다음 주에도 많이 와주세요."),
        ("더블스 파트너 구합니다", "매주 수요일 저녁 6시에 더블스 치실 분!"),
        ("테니스 엘보 치료법", "팔꿈치가 아프네요. 스트레칭 방법 아시는 분?"),
    ],
    2: [
        ("미국에서 김치찌개 맛있게 끓이기", "비법: 잘 익은 김치 + 돼지고기 + 다시다\n1. 참기름에 김치 볶기\n2. 돼지고기 넣고 같이 볶기\n3. 물 붓고 끓이기\n4. 두부, 파 넣기"),
        ("Costco 삼겹살 에어프라이어 구이", "에어프라이어 380도 20분이면 바삭! $8.99 삼겹살 최고."),
        ("반찬 만들기 모임 후기", "5가지 반찬 나눠서 한 달 치 완성! 다음 달도 해요~"),
        ("TJ 재료로 만든 한식 모음", "TJ frozen rice + 참기름 + 계란 = 볶음밥!"),
        ("추석 송편 같이 만들어요!", "재료비 나눠서 같이 만들 분 모집합니다."),
        ("에어프라이어 치킨 성공!", "밀가루+전분+파프리카 380도 25분 = 완벽"),
    ],
    3: [
        ("4월 선정 도서: 파친코", "모임: 4월 15일 토 오후 3시\n장소: Fort Lee 카페\n읽고 오셔서 감상 나눠요!"),
        ("3월 모임 후기 - 아몬드", "손원평 작가 아몬드 토론했어요. 감정에 대해 깊이 생각해보게 됐습니다."),
        ("추천 도서 목록", "1. 82년생 김지영\n2. 불편한 편의점\n3. 달러구트 꿈 백화점\n4. 파친코"),
        ("영어 원서 읽기도 해볼까요?", "한국어 책만 말고 영어 원서도 같이 읽으면 어떨까요?"),
    ],
    4: [
        ("이번 주 스터디: React 19", "React 19 새 기능 같이 공부! 수요일 저녁 7시 줌\nServer Components, Actions, use() hook"),
        ("구글 면접 스터디 모집", "주 2회 LeetCode + mock interview. 관심 있으신 분?"),
        ("연봉 정보 공유 (익명)", "시니어 TC기준:\n구글 L5: $350-450K\n메타 E5: $380-480K\n애플 ICT4: $320-400K"),
        ("레이오프 후 취업 성공기", "6개월 만에 새 직장! LinkedIn 최적화가 핵심이었어요."),
        ("사이드 프로젝트 같이 하실 분", "한인 커뮤니티 앱 만들기 프로젝트!"),
        ("AI 트렌드 토론회", "ChatGPT, Claude 등 LLM 관련 토론 모임합니다."),
    ],
    5: [
        ("벚꽃 시즌 출사 모임!", "워싱턴 DC Tidal Basin 벚꽃 촬영 다녀왔어요!"),
        ("초보 카메라 추천", "소니 A6400: 가성비\n캐논 R50: 초보 친화\n후지 X-T30: 색감"),
        ("야경 사진 팁", "삼각대 필수, ISO 낮게, 셔터 느리게, f/8-11"),
        ("가을 단풍 출사 모임 공지", "이번 주말 Central Park! 카메라 없어도 폰카 OK"),
    ],
    6: [
        ("이번 주 말씀: 로마서 8장", "금요일 저녁 7시 줌으로 모여요. 미리 읽어오시면 좋겠습니다."),
        ("부활절 연합 예배 + 점심", "부활절 후 점심 식사 모임! 참석 여부 알려주세요."),
        ("새가족 환영합니다!", "교파 상관없이 함께 성경공부하는 모임이에요."),
    ],
    7: [
        ("K-Town 새 양꼬치집 후기", "가격 착하고 맛있었어요! 양꼬치 + 마라탕 조합 최고"),
        ("플러싱 숨은 맛집 리스트", "1. 한국관 설렁탕\n2. 함흥 냉면\n3. 마라탕 골목"),
        ("브루클린 브런치 카페 추천", "주말 브런치 하기 좋은 곳 5곳!"),
        ("홈파티 불고기 레시피", "10인분 Costco 불고기 양념이면 간단!"),
    ],
    8: [
        ("Bear Mountain 등산 모임", "토요일 8시 출발! 왕복 4시간, 난이도 중\n준비물: 등산화, 물 2L, 간식"),
        ("등산화 추천", "Merrell Moab 3: $130, 가성비 최고\nSalomon X Ultra: $150"),
        ("Breakneck Ridge 후기", "힘들었지만 허드슨 강 뷰가 최고!"),
        ("초보 하이킹 코스 추천 (동부)", "1. Harriman\n2. Minnewaska\n3. Storm King"),
        ("5월 캠핑 같이 가실 분!", "1박 2일 캠핑 계획 중. 관심 있으시면 댓글!"),
    ],
    9: [
        ("이번 주 라운딩 (Bethpage)", "일요일 7:30 티타임. 그린피 $65 + 카트 $20"),
        ("드라이버 비거리 늘리기", "레슨 프로 팁: 어드레스 자세, 백스윙 꼬임, 하체 먼저"),
        ("골프 초보 가이드", "중고 클럽 세트 $200-300으로 시작!\n레인지에서 연습 후 코스 도전"),
        ("한인 골프 대회 6월!", "참가비 $120 (그린피+식사). 신청 서두르세요!"),
    ],
    10: [
        ("2026년 미국 주식 전망", "AI 관련주 계속 오를까? 조정 올까? 토론해요!"),
        ("부동산 vs 주식 $50K", "여유자금 $50K 어디 투자? 의견 부탁!"),
        ("401K 포트폴리오 공유", "S&P 500: 60%, 해외: 20%, 채권: 15%, REIT: 5%"),
        ("비트코인 홀딩 중인데...", "$30K에 샀는데 여러분은 어떻게 보세요?"),
    ],
}

comments = [
    "좋은 정보 감사합니다!", "다음에 꼭 참석할게요!", "저도 같이 하고 싶어요!",
    "매번 좋은 모임 감사합니다 ㅎㅎ", "초보인데 가도 괜찮을까요?", "재밌었어요! 다음에도 올게요",
    "사진 더 올려주세요!", "정모 때 뵙겠습니다!", "좋아요~ 기대됩니다!",
    "저도 참여합니다!", "아 그날 일이 있어서 아쉽네요 ㅠ", "대박이네요!",
    "오 이거 몰랐네요", "감사합니다 도움 많이 됐어요", "다음에 같이 가요!",
]

cur.execute("DELETE FROM club_posts")
cur.execute("DELETE FROM club_members WHERE club_id <= 12")
total_p = 0
total_m = 0

for club_id, club_name in clubs:
    if club_id > 12: continue
    num_mem = random.randint(15, 40)
    mem_users = random.sample(USER_IDS, num_mem)
    cur.execute(f"INSERT IGNORE INTO club_members (club_id, user_id, role, status, created_at) VALUES ({club_id}, {mem_users[0]}, 'owner', 'approved', '{rand_date(12)}')")
    for i, uid in enumerate(mem_users[1:]):
        role = 'admin' if i < 2 else 'member'
        cur.execute(f"INSERT IGNORE INTO club_members (club_id, user_id, role, status, created_at) VALUES ({club_id}, {uid}, '{role}', 'approved', '{rand_date(10)}')")
    total_m += num_mem
    cur.execute(f"UPDATE clubs SET member_count = {num_mem} WHERE id = {club_id}")

    posts = club_posts.get(club_id, [])
    for title, content in posts:
        uid = random.choice(mem_users)
        cd = rand_date(4)
        cur.execute(f"""INSERT INTO club_posts (club_id, user_id, title, content, view_count, like_count, created_at, updated_at)
            VALUES ({club_id}, {uid}, '{esc(title)}', '{esc(content)}', {random.randint(20,500)}, {random.randint(0,30)}, '{cd}', '{cd}')""")
        total_p += 1
    print(f"  Club {club_id}: {num_mem} members, {len(posts)} posts")

print(f"\nDone: {total_m} members, {total_p} posts")
for t in ["clubs", "club_members", "club_posts"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]}")
conn.close()
