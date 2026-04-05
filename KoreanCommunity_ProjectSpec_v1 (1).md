# 한인 커뮤니티 통합 플랫폼 — 프로젝트 기획서 v1.0
> Claude Code 작업용 마스터 문서  
> 호스팅: DigitalOcean | 언어: PHP 8.x + MySQL 8 + WebSocket  
> 작성일: 2026-03-27

---

## 1. 프로젝트 개요

### 플랫폼명
**SomeKorean** — 미국 내 한인 커뮤니티 통합 포털

### 도메인
```
메인 도메인 : somekorean.com
서버 hostname: somekorean-server
앱 이름     : SomeKorean
앱 ID       : com.somekorean.app (iOS/Android 번들 ID)
```

### 컨셉
헤이코리안 + 미씨USA + GTKSA의 장점을 통합하고,  
**라이드셰어(알바 라이드) · 게임/포인트 · 매칭 · 노인알림 · 실시간 채팅**을 더한  
미국 한인 올인원 생활 플랫폼

### 핵심 차별점
1. **알바 라이드** — 우버 방식 비전문 드라이버 라이드 서비스 (실시간 지도)
2. **게임 & 포인트** — 고스톱/포커 → 포인트 → 사이트 캐시
3. **나이별 매칭** — 신분증 인증 + AI 스캠 방지
4. **노인 안심 알림** — 미응답 시 자녀 자동 연락
5. **지역/테마 단톡방** — 24시간 WebSocket 실시간 채팅

---

## 2. 기술 스택 & 인프라

### DigitalOcean 구성
```
Droplet        : Ubuntu 22.04 LTS  (최소 4GB RAM / 2 vCPU 권장)
Database       : DigitalOcean Managed MySQL 8
Redis           : DigitalOcean Managed Redis (채팅 큐 + 세션)
Spaces         : S3 호환 오브젝트 스토리지 (이미지·파일)
Load Balancer  : (트래픽 증가 시 추가)
Domain         : Namecheap 또는 DO Domains (도메인 등록)
SSL            : Let's Encrypt (Certbot 자동갱신)
```

### 백엔드
```
언어   : PHP 8.2
프레임워크: Laravel 11 (API) + 일부 순수 PHP
WebSocket : Ratchet PHP (채팅 + 라이드 실시간 위치)
인증   : JWT (tymon/jwt-auth) + 이메일 인증
큐     : Laravel Queue + Redis
스케줄러: Laravel Scheduler (노인 체크인 크론)
결제   : Stripe API (캐시 충전 · 광고비)
SMS/전화: Twilio API (노인 알림 · 인증 문자)
지도   : Google Maps API (라이드 서비스)
푸시   : Firebase FCM (모바일 푸시)
이미지 처리: Intervention Image
```

### 프론트엔드
```
프레임워크: Vue.js 3 (Composition API)
번들러  : Vite
CSS    : Tailwind CSS v3
지도   : Google Maps JavaScript API + Marker Clustering
WebSocket 클라이언트: Laravel Echo + Socket.io
PWA    : Vite PWA Plugin (모바일 홈화면 설치)
다국어 : Vue i18n (한국어 · 영어)
```

### 서버 구성 (DigitalOcean Droplet)
```
Nginx          : 리버스 프록시 + SSL
PHP-FPM 8.2   : Laravel 앱
Node.js 18     : WebSocket 서버 포트 (6001)
Supervisor     : WebSocket 프로세스 관리
Certbot        : SSL 자동 갱신
UFW 방화벽    : 80, 443, 6001 포트 오픈
```

### WebSocket 포트 설정 (DO 방화벽 필수 오픈)
```
80   → HTTP (Nginx → HTTPS 리다이렉트)
443  → HTTPS (메인 앱)
6001 → WebSocket (Ratchet / Laravel Echo Server)
3306 → MySQL (내부 네트워크만)
6379 → Redis (내부 네트워크만)
```

---

## 3. 전체 사이트맵

```
/ (홈)
├── /auth
│   ├── /register          # 회원가입 (이메일 인증)
│   ├── /login             # 로그인
│   ├── /forgot-password   # 비밀번호 찾기
│   └── /verify/:token     # 이메일 인증 링크
│
├── /community             # 커뮤니티 (포럼)
│   ├── /board             # 전체 게시판 목록
│   │   ├── /free          # 자유게시판
│   │   ├── /parenting     # 육아
│   │   ├── /beauty        # 뷰티 / 패션
│   │   ├── /health        # 건강 / 의료
│   │   ├── /travel        # 여행
│   │   ├── /food          # 음식 / 레시피
│   │   ├── /education     # 교육 / 유학
│   │   ├── /immigration   # 이민 / 정착 정보
│   │   ├── /finance       # 재정 / 투자
│   │   ├── /jobs-talk     # 취업 이야기
│   │   └── /local/:region # 지역별 게시판 (Atlanta, NY, LA...)
│   ├── /post/:id          # 게시글 상세
│   ├── /write             # 글쓰기
│   ├── /blog              # 개인 블로그
│   │   ├── /:username     # 유저 블로그 홈
│   │   └── /:username/:postId  # 블로그 글
│   └── /expert-column     # 전문가 칼럼 (이민, 법률, 의료, 재정)
│
├── /jobs                  # 구인 / 구직
│   ├── /list              # 채용공고 목록
│   ├── /post/:id          # 채용공고 상세
│   ├── /write             # 채용공고 등록
│   ├── /resume            # 이력서 목록
│   ├── /resume/write      # 이력서 작성
│   └── /resume/:id        # 이력서 상세
│
├── /market                # 마켓플레이스
│   ├── /used              # 중고 사고팔기
│   │   ├── /list          # 목록
│   │   ├── /post/:id      # 상세
│   │   └── /write         # 등록
│   ├── /real-estate       # 부동산 / 렌트
│   │   ├── /list
│   │   ├── /post/:id
│   │   └── /write
│   ├── /cars              # 자동차 거래
│   │   ├── /list
│   │   ├── /post/:id
│   │   └── /write
│   └── /shop              # 한인 쇼핑몰 (뷰티·식품 등)
│       ├── /list
│       ├── /product/:id
│       └── /cart
│
├── /ride                  # ★ 알바 라이드 서비스
│   ├── /                  # 메인 (지도 + 콜 요청)
│   ├── /request           # 승객 - 라이드 요청
│   ├── /track/:rideId     # 승객 - 실시간 드라이버 추적
│   ├── /history           # 내 이용 내역
│   ├── /driver            # 드라이버 전용
│   │   ├── /register      # 드라이버 등록 (면허 + 차량 인증)
│   │   ├── /dashboard     # 대시보드 (수입·콜 현황)
│   │   ├── /online        # 온라인 전환 + 콜 대기 지도
│   │   └── /history       # 운행 이력
│   └── /admin             # 라이드 관리자 (관리자 전용)
│
├── /games                 # ★ 게임 & 포인트
│   ├── /lobby             # 게임 로비 (목록)
│   ├── /go-stop           # 고스톱 (WebSocket 멀티플레이)
│   ├── /poker             # 텍사스 홀덤
│   ├── /quiz              # 일일 퀴즈
│   ├── /leaderboard       # 리더보드 (주간/월간)
│   ├── /points            # 내 포인트 현황
│   │   ├── /history       # 적립/차감 이력
│   │   └── /exchange      # 포인트 → 캐시 전환
│   └── /shop              # 포인트샵 (쿠폰 교환)
│
├── /match                 # ★ 나이별 매칭
│   ├── /                  # 매칭 메인 (소개 + 인증 유도)
│   ├── /verify            # 신분증 업로드 인증
│   ├── /profile/setup     # 매칭 프로필 작성
│   ├── /browse            # 상대방 카드 보기 (Tinder 스타일)
│   ├── /likes             # 받은 / 보낸 좋아요
│   ├── /matches           # 매칭된 상대 목록
│   ├── /chat/:matchId     # 매칭 1:1 채팅
│   └── /settings          # 매칭 설정 (나이 범위, 지역, 공개 범위)
│
├── /elder                 # ★ 노인 안심 서비스
│   ├── /                  # 서비스 소개
│   ├── /checkin           # 노인 본인 - 체크인 화면 (큰 UI)
│   ├── /sos               # SOS 긴급 버튼
│   ├── /guardian          # 보호자 대시보드
│   │   ├── /register      # 보호자 등록 + 연결 코드 입력
│   │   ├── /dashboard     # 체크인 현황 모니터링
│   │   ├── /calendar      # 체크인 기록 달력
│   │   └── /settings      # 알림 설정 (시간·빈도)
│   └── /medicine          # 약 복용 알림 관리
│
├── /chat                  # ★ 단톡방 시스템
│   ├── /                  # 채팅 홈 (방 목록)
│   ├── /local             # 지역별 채팅방
│   │   ├── /atlanta
│   │   ├── /suwanee
│   │   ├── /johns-creek
│   │   ├── /new-york
│   │   ├── /los-angeles
│   │   ├── /dallas
│   │   └── /chicago
│   ├── /open              # 24시간 전국 오픈채팅
│   ├── /theme/:tag        # 테마별 채팅 (#주식 #육아 #맛집...)
│   ├── /room/:roomId      # 채팅방 입장
│   └── /dm/:userId        # 1:1 다이렉트 메시지
│
├── /directory             # 한인 업소록
│   ├── /                  # 업소록 홈 (카테고리 + 지역 검색)
│   ├── /category/:cat     # 카테고리별 (식당·미용·법률·의료...)
│   ├── /business/:id      # 업체 상세 + 리뷰
│   ├── /register          # 업체 등록
│   └── /manage            # 업체 관리 (업주 전용)
│
├── /events                # 이벤트 & 모임
│   ├── /                  # 이벤트 목록 + 달력 뷰
│   ├── /event/:id         # 이벤트 상세
│   ├── /create            # 이벤트 등록
│   ├── /meetup            # 모임 게시판
│   └── /restaurant        # 음식점 추천 (지역별)
│
├── /education             # 교육 & 수업
│   ├── /classes           # 수업 / 과외 목록
│   ├── /class/:id         # 수업 상세
│   ├── /scholarship       # 장학금 정보
│   └── /tutors            # 과외 선생님 목록
│
├── /news                  # 뉴스
│   ├── /                  # 뉴스 홈
│   ├── /article/:id       # 기사 상세
│   └── /category/:cat     # 카테고리별 뉴스
│
├── /profile               # 내 프로필
│   ├── /:username         # 공개 프로필
│   ├── /edit              # 프로필 수정
│   ├── /points            # 포인트/캐시 현황
│   ├── /level             # 회원 등급 현황
│   ├── /activity          # 활동 내역
│   ├── /bookmarks         # 북마크한 글
│   └── /notifications     # 알림 설정
│
├── /messages              # 메시지 (구 쪽지)
│   ├── /inbox             # 받은 메시지
│   └── /compose/:userId   # 메시지 보내기
│
├── /search                # 통합 검색
│   └── /results?q=        # 검색 결과 (게시글·업소·사람)
│
├── /admin                 # 관리자 (admin 전용)
│   ├── /dashboard         # 통계 대시보드
│   ├── /users             # 회원 관리
│   ├── /posts             # 게시글 관리
│   ├── /reports           # 신고 처리
│   ├── /ads               # 광고 관리
│   ├── /ride              # 라이드 운행 모니터링
│   ├── /match             # 매칭 관리 + 스캠 신고
│   ├── /elder             # 노인 알림 상태
│   └── /points            # 포인트 관리
│
└── /settings              # 계정 설정
    ├── /account           # 계정 정보
    ├── /security          # 비밀번호 · 2FA
    ├── /notifications     # 알림 수신 설정
    ├── /privacy           # 개인정보 설정
    ├── /language          # 언어 설정 (한/영)
    └── /billing           # 결제 수단 · 청구 내역
```

---

## 4. 알바 라이드 서비스 상세 기획

### 개요
- 우버 방식의 P2P 라이드셰어
- 전문 택시 불필요 — 일반인 드라이버 (알바 개념)
- 실시간 지도에 드라이버 위치 표시
- 한인 커뮤니티 내 신뢰 기반 (실명 인증)

### 승객 플로우
```
1. 앱 열기 → 지도에 주변 드라이버 점으로 표시 (실시간)
2. 출발지 · 목적지 입력
3. 예상 금액 · 시간 확인
4. 콜 요청 → 주변 드라이버에게 푸시 알림 발송
5. 드라이버 수락 → 매칭 완료 알림
6. 실시간 드라이버 위치 추적 (WebSocket)
7. 탑승 → 목적지 도착
8. 자동 결제 (카드 · 캐시) + 별점 평가
```

### 드라이버 플로우
```
1. 드라이버 등록: 면허증 업로드 + 차량 등록 + 신원 인증
2. 앱에서 [온라인] 전환 → 지도에 본인 위치 표시 시작
3. 콜 요청 알림 수신 → 지도에 승객 위치 + 요금 표시
4. [수락] 또는 [패스] 선택 (30초 타임아웃)
5. 수락 시 승객에게 도착 ETA 전송
6. 탑승 → 목적지 안내 (Google Maps 연동)
7. 완료 → 수입 적립 + 별점 받기
```

### 실시간 기술 구현
```
- WebSocket (Ratchet PHP): 드라이버 GPS 위치 1초마다 broadcast
- Google Maps API: 지도 렌더링 + 경로 안내
- Geolocation API: 브라우저/앱 위치 권한
- Haversine 공식: 반경 N km 내 드라이버 필터링
- Redis Pub/Sub: 채널 분리 (ride:{rideId} 채널)
- Twilio: 매칭 SMS 알림
```

### DB 테이블 (라이드)
```sql
rides
  id, passenger_id, driver_id, status(requesting/matched/ongoing/done/cancelled),
  pickup_lat, pickup_lng, pickup_address,
  dropoff_lat, dropoff_lng, dropoff_address,
  estimated_fare, final_fare, payment_method,
  requested_at, matched_at, started_at, completed_at

driver_profiles
  user_id, license_number, license_img, car_make, car_model,
  car_year, car_color, car_plate, verified, is_online,
  current_lat, current_lng, last_location_at, rating_avg

ride_reviews
  id, ride_id, reviewer_id, reviewed_id, rating(1-5), comment

driver_locations (Redis 캐시 우선, DB 백업)
  driver_id, lat, lng, updated_at
```

### 요금 구조
```
기본요금      : $3.00
거리요금      : $1.20/mile
시간요금      : $0.20/min (정체 시)
플랫폼 수수료  : 15% (드라이버 수입의 85%)
최소요금      : $5.00
야간 할증 (11pm-6am) : 1.2x
```

---

## 5. 게임 & 포인트 시스템 상세

### 포인트 적립 테이블
```
출석체크        : 10P / 일  (연속 7일: +50P 보너스)
게시글 작성     : 30P
댓글 작성       : 5P  (일 최대 50P)
받은 추천       : 10P / 개
게임 승리       : 50~500P (게임종류·판돈에 따라)
일일 퀴즈 정답  : 20P
신규 회원 추천  : 500P
라이드 이용     : 20P
매칭 프로필 인증: 200P (최초 1회)
블로그 조회 1000건: 100P
```

### 포인트 → 캐시 전환
```
1,000P = $1.00 사이트 캐시
최소 전환 단위 : 5,000P ($5)
전환 한도      : 월 50,000P ($50) 제한
캐시 사용처    : 광고 게시, 매칭 프리미엄, 라이드 결제 일부, 포인트샵
현금 환전      : 불가 (법적 이슈 방지)
```

### 게임 구현
```
고스톱  : 3인 멀티플레이 / WebSocket / 화투 카드 SVG 렌더링
맞고    : 2인 매칭 / 빠른 대전
포커    : 6인 텍사스 홀덤 / 칩은 무료 지급
일일 퀴즈: 한국 문화 · 미국 생활 / 개인 플레이 / 오전 9시 리셋
```

---

## 6. 나이별 매칭 상세

### 인증 플로우
```
1단계: 이메일 인증 (가입 시)
2단계: 전화번호 SMS 인증
3단계: 신분증 업로드 (Driver's License 앞면)
       → AWS Rekognition 또는 Stripe Identity API로 인증
4단계: 셀피 + 신분증 동시 사진 (Liveness Check)
5단계: 관리자 수동 검토 (24시간 내)
→ 인증 배지 발급
```

### 스캠 방지 알고리즘
```
- 프로필 사진 Google Vision API 역방향 검색
- 메시지에 전화번호/이메일/SNS 포함 시 경고 + 마스킹
- "돈", "wire transfer", "gift card" 키워드 자동 감지
- 신고 2회: 자동 매칭 일시 정지
- 신고 5회: 계정 정지 + 관리자 검토
```

### 연령대 구분
```
20대 (20-29) / 30대 (30-39) / 40대 (40-49)
50대 (50-59) / 시니어 (60+) — 별도 UI (큰 글씨)
기본 설정: ±7세 범위  |  사용자 조정: ±0~15세
```

---

## 7. 노인 안심 알림 상세

### 알림 플로우
```
설정 시간 도달
  → 앱 푸시 알림: "안녕하세요! 오늘도 건강하세요? [괜찮아요] 버튼"
  → 30분 무응답: 2차 푸시 알림
  → 60분 무응답: Twilio SMS → 보호자1 휴대폰
  → 90분 무응답: Twilio 자동 전화 → 보호자1
  → 미응답: Twilio 전화 → 보호자2
  → 최후: 관리자 알림 대시보드 표시
```

### 크론 스케줄러 (Laravel Scheduler)
```php
// app/Console/Kernel.php
$schedule->command('elder:check')->everyMinute();
// ElderCheckCommand: 응답 미수신 노인 목록 조회 → 알림 발송
```

### SOS 버튼
```
홈화면 큰 빨간 버튼 (접근성 고려)
3초 누르면 발동 (오작동 방지)
→ GPS 위치 + 현재 시간 → 보호자 SMS/전화
→ 선택적: 119 자동 연결
→ 커뮤니티 채팅방에도 알림 가능 (설정 시)
```

---

## 8. 단톡방 시스템 상세

### 채팅방 종류
```
지역 고정방 (자동 배정)
  - 가입 시 주소 입력 → 해당 지역방 자동 가입
  - Atlanta / Suwanee / Johns Creek / Duluth / Alpharetta
  - New York / New Jersey / Los Angeles / Dallas / Chicago / Seattle

테마방 (자유 가입)
  - #주식투자 #부동산 #창업 #육아 #맛집 #운동 #유학 #이민

오픈채팅 (전국)
  - 24시간 전국 한인 실시간 대화
  - 익명 닉네임 사용 가능
  - 메시지 24시간 보관 후 자동 삭제

1:1 DM
  - 친구 추가 또는 게시글에서 바로 DM
  - 라이드 매칭 후 자동 DM 방 생성
  - 매칭 서비스 채팅과 통합
```

### WebSocket 서버 설정
```
포트: 6001 (DigitalOcean 방화벽 오픈 필요)
서버: Ratchet PHP 또는 Laravel Reverb (최신)
클라이언트: Laravel Echo + Pusher JS
채널 구조:
  presence-chat.room.{roomId}   — 채팅방 (접속자 목록 포함)
  private-dm.{userId}           — 1:1 DM
  private-ride.{rideId}         — 라이드 실시간 추적
  presence-game.{gameId}        — 게임 방
  private-elder.{guardianId}    — 노인 알림
```

---

## 9. 회원 등급 시스템

```
씨앗    : 가입 ~ 999P        (기본 기능)
새싹    : 1,000 ~ 4,999P    (블로그 개설 가능)
나무    : 5,000 ~ 19,999P   (광고 할인 10%, 매칭 무제한)
숲      : 20,000 ~ 49,999P  (광고 할인 20%, 전용 게시판)
참나무  : 50,000P+           (VIP 전용 혜택, 리더보드 특별 표시)
```

---

## 10. 핵심 DB 스키마

### users
```sql
id, username, email, password, phone, avatar,
region(지역), address, lat, lng,
level(씨앗/새싹/나무/숲/참나무),
points_total, cash_balance,
email_verified_at, phone_verified_at,
is_elder(bool), is_driver(bool),
lang(ko/en), status(active/banned),
created_at, updated_at
```

### posts
```sql
id, board_id, user_id, title, content, thumbnail,
view_count, like_count, comment_count,
is_pinned, is_notice, status,
created_at, updated_at
```

### point_logs
```sql
id, user_id, type(earn/spend/convert),
action(checkin/game_win/post/referral/convert...),
amount, balance_after, ref_id, memo,
created_at
```

### match_profiles
```sql
id, user_id, nickname, gender, birth_year,
age_range_min, age_range_max, region,
bio, interests(JSON), photos(JSON),
verified(bool), visibility(public/matches/hidden),
created_at, updated_at
```

### match_verifications
```sql
id, user_id, id_front_img, selfie_img,
verified_at, verified_by(admin_id), status
```

### elder_settings
```sql
id, user_id, checkin_times(JSON),
alert_delay_min(default 60),
guardians(JSON: [{name, phone, relation, priority}]),
sos_contacts(JSON), last_checkin_at, status
```

### chat_rooms
```sql
id, type(local/theme/open/dm),
name, tag, region, icon, description,
max_members, created_by, created_at
```

### chat_messages
```sql
id, room_id, user_id, content, type(text/image/system),
is_anonymous, is_deleted, created_at
```

### rides
```sql
id, passenger_id, driver_id,
status(requesting/matched/ongoing/completed/cancelled),
pickup_lat, pickup_lng, pickup_address,
dropoff_lat, dropoff_lng, dropoff_address,
estimated_fare, final_fare, platform_fee,
payment_method, rating_driver, rating_passenger,
requested_at, matched_at, started_at, completed_at
```

### businesses (업소록)
```sql
id, owner_id, name, category, description,
address, lat, lng, phone, website,
hours(JSON), photos(JSON), rating_avg,
is_verified, is_sponsored, status,
created_at, updated_at
```

---

## 11. API 엔드포인트 구조

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout

GET    /api/posts?board=&page=
POST   /api/posts
GET    /api/posts/{id}
PUT    /api/posts/{id}
DELETE /api/posts/{id}
POST   /api/posts/{id}/like

GET    /api/jobs?page=
POST   /api/jobs
GET    /api/jobs/{id}

GET    /api/market/used?page=
POST   /api/market/used
GET    /api/market/real-estate?region=

POST   /api/ride/request
GET    /api/ride/{id}
POST   /api/ride/{id}/cancel
POST   /api/ride/{id}/complete
GET    /api/ride/drivers/nearby?lat=&lng=  (드라이버 목록)
POST   /api/driver/location               (위치 업데이트)
POST   /api/driver/online                 (온라인 전환)
POST   /api/ride/{id}/accept              (드라이버 수락)

GET    /api/match/browse?page=
POST   /api/match/like/{userId}
GET    /api/match/matches
POST   /api/match/verify (신분증 업로드)

GET    /api/points/balance
GET    /api/points/history
POST   /api/points/convert              (포인트 → 캐시)

GET    /api/elder/settings
PUT    /api/elder/settings
POST   /api/elder/checkin               (체크인 응답)
POST   /api/elder/sos                   (SOS 발동)

GET    /api/chat/rooms
POST   /api/chat/rooms/{id}/join
GET    /api/chat/rooms/{id}/messages
POST   /api/chat/messages               (메시지 전송)

GET    /api/businesses?category=&region=&page=
POST   /api/businesses
GET    /api/businesses/{id}
POST   /api/businesses/{id}/review

GET    /api/events?region=&page=
POST   /api/events

GET    /api/search?q=&type=

GET    /api/admin/stats                 (관리자)
GET    /api/admin/reports
POST   /api/admin/users/{id}/ban
```

---

## 12. 광고 수익 모델

```
배너 광고
  - 메인 상단 배너    : $300/월
  - 카테고리 배너     : $150/월
  - 모바일 인터스티셜 : $100/월

업소록 프리미엄
  - 일반 등록    : 무료
  - 프리미엄 노출: $50/월 (상단 고정)
  - 스폰서 배지  : $80/월

게시글 상단 고정
  - 구인/구직     : $20/7일
  - 중고/부동산   : $15/7일

라이드 플랫폼 수수료: 15%

매칭 프리미엄
  - 무제한 좋아요  : $9.99/월
  - 프로필 부스트  : $2.99/24시간

캐시 직접 충전
  - $5 / $10 / $20 / $50 충전 (Stripe)
```

---

## 13. 개발 우선순위 (Phase)

### Phase 1 — MVP (3개월)
```
[ ] DigitalOcean 서버 세팅 (Nginx + PHP + MySQL + Redis)
[ ] Laravel 프로젝트 초기화 + 도메인 SSL 설정
[ ] 회원가입 / 로그인 / 이메일 인증
[ ] 기본 게시판 (자유/지역/카테고리)
[ ] 구인구직 게시판
[ ] 중고 장터
[ ] 한인 업소록 기본
[ ] 포인트 기본 (출석체크·게시글)
[ ] 1:1 DM (기본)
[ ] 관리자 기본 대시보드
```

### Phase 2 — 핵심 기능 (2개월)
```
[ ] WebSocket 서버 구축 (Laravel Reverb 또는 Ratchet)
[ ] 지역별·테마별 단톡방
[ ] 24시간 오픈채팅
[ ] 일일 퀴즈 게임 + 포인트 전환
[ ] 노인 안심 알림 (크론 + Twilio)
[ ] 보호자 대시보드
[ ] 모바일 PWA 설치
```

### Phase 3 — 알바 라이드 (2개월)
```
[ ] Google Maps API 연동
[ ] 드라이버 등록 · 인증
[ ] 콜 요청 · 수락 · 취소 플로우
[ ] 실시간 위치 추적 (WebSocket)
[ ] 결제 연동 (Stripe)
[ ] 리뷰·별점 시스템
```

### Phase 4 — 게임 & 매칭 (2개월)
```
[ ] 고스톱 WebSocket 멀티플레이
[ ] 텍사스 홀덤
[ ] 매칭 신분증 인증 (Stripe Identity)
[ ] 매칭 AI 스캠 필터
[ ] 매칭 카드 UI (Tinder 스타일 Swipe)
[ ] 포인트샵
[ ] 리더보드
```

### Phase 5 — 고도화 (지속)
```
[ ] AI 검색 (OpenAI 연동)
[ ] 추천 알고리즘 (포스트·업소·매칭)
[ ] 음성 채팅 (WebRTC)
[ ] 이커머스 쇼핑몰 완성
[ ] 다국어 확장 (스페인어 추가)
[ ] iOS / Android 네이티브 앱 (React Native)
```

---

## 14. 보안 체크리스트

```
[ ] HTTPS 강제 (HSTS)
[ ] SQL Injection 방지 (Laravel Eloquent ORM)
[ ] XSS 방지 (Blade {{ }} 자동 이스케이프)
[ ] CSRF 토큰 (모든 폼)
[ ] Rate Limiting (API: 60req/min, 로그인: 5회/분)
[ ] 파일 업로드 검증 (MIME 타입 + 크기 제한)
[ ] 민감 정보 암호화 저장 (신분증 이미지, 전화번호)
[ ] 2FA 옵션 (매칭·라이드 드라이버 필수)
[ ] VPN/프록시 감지 (매칭 서비스)
[ ] 관리자 IP 화이트리스트
[ ] 정기 DB 백업 (DO Managed DB 자동 스냅샷)
[ ] 에러 로그 Slack 알림 (Monolog)
```

---

## 15. DigitalOcean 초기 세팅 가이드

### 서버 생성
```bash
# Droplet: Ubuntu 22.04 LTS / 4GB RAM / 2vCPU / 80GB SSD
# 지역: New York 또는 San Francisco (미국 서부)
# SSH Key 등록 필수

# 초기 접속
ssh root@YOUR_DROPLET_IP

# 패키지 업데이트
apt update && apt upgrade -y

# Nginx 설치
apt install nginx -y

# PHP 8.2 설치
apt install php8.2 php8.2-fpm php8.2-mysql php8.2-redis \
  php8.2-curl php8.2-mbstring php8.2-xml php8.2-zip \
  php8.2-gd php8.2-bcmath -y

# Composer 설치
curl -sS https://getcomposer.org/installer | php
mv composer.phar /usr/local/bin/composer

# Node.js 18 설치 (Vue.js 빌드용)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y

# Supervisor 설치 (WebSocket 프로세스 관리)
apt install supervisor -y
```

### Nginx WebSocket 설정
```nginx
# /etc/nginx/sites-available/somekorean
server {
    listen 443 ssl;
    server_name somekorean.com;

    # WebSocket 프록시
    location /app {
        proxy_pass http://localhost:6001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 60s;
    }

    location / {
        root /var/www/somekorean/public;
        try_files $uri $uri/ /index.php?$query_string;
    }
}
```

### Supervisor WebSocket 설정
```ini
# /etc/supervisor/conf.d/reverb.conf
[program:reverb]
command=php /var/www/somekorean/artisan reverb:start
directory=/var/www/somekorean
autostart=true
autorestart=true
user=www-data
redirect_stderr=true
stdout_logfile=/var/log/reverb.log
```

### 환경변수 (.env 핵심 항목)
```
APP_URL=https://somekorean.com

DB_HOST=your-do-mysql-host
DB_DATABASE=somekorean
DB_USERNAME=somekorean_user
DB_PASSWORD=strong_password

REDIS_HOST=your-do-redis-host
REDIS_PASSWORD=redis_password

REVERB_APP_ID=your_app_id
REVERB_APP_KEY=your_app_key
REVERB_APP_SECRET=your_secret
REVERB_HOST=somekorean.com
REVERB_PORT=443
REVERB_SCHEME=https

GOOGLE_MAPS_API_KEY=your_key
STRIPE_KEY=your_stripe_key
STRIPE_SECRET=your_stripe_secret
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_FROM=+1XXXXXXXXXX
FIREBASE_CREDENTIALS=path/to/firebase.json

AWS_ACCESS_KEY_ID=do_spaces_key
AWS_SECRET_ACCESS_KEY=do_spaces_secret
AWS_DEFAULT_REGION=nyc3
AWS_BUCKET=somekorean-media
AWS_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

---

## 16. 추가 권장 기능 (미래 확장)

```
추천 피드    : 내 관심사·지역 기반 게시글 자동 추천
영상 통화    : WebRTC 1:1 영상통화 (매칭 + 보호자-노인)
그룹 라이드  : 카풀 기능 (같은 방향 여러 승객)
음식 배달    : 로컬 한식당 배달 연결 (DoorDash 제휴 또는 자체)
라이브 방송  : 실시간 커뮤니티 라이브 (요리·뷰티 등)
NFT 뱃지    : 특별 활동 기념 디지털 배지
AI 번역     : 영어↔한국어 게시글 자동 번역
한인 뉴스봇  : 주요 한인 언론 RSS 자동 수집
공동구매     : 그룹 바이 게시판
멘토링 매칭  : 선배-후배 비즈니스 멘토 연결
```

---

## 17. 모바일 앱 기본 방향 (iOS / Android)

### 개발 방식
```
React Native (Expo 또는 Bare Workflow)
  - iOS · Android 코드베이스 80%+ 공유
  - 웹(Laravel+Vue)과 동일한 REST API + WebSocket 사용
  - 앱스토어 / 구글플레이 동시 배포
  - PWA는 보조 수단 (앱 설치 전 접근용)
```

### 핵심 라이브러리
```
지도          : react-native-maps (Google Maps SDK)
WebSocket     : socket.io-client
푸시알림      : @react-native-firebase/messaging (FCM)
위치          : expo-location (GPS 실시간)
카메라/파일   : expo-image-picker (신분증 업로드, 매칭 사진)
결제          : react-native-stripe-sdk
알림          : expo-notifications
로컬 저장     : @react-native-async-storage
인증          : expo-local-authentication (Face ID / 지문)
```

---

## 18. 모바일 앱 홈 화면 와이어프레임

### 공통 화면 구성 (위→아래 스크롤)
```
[상단 앱바]
  로고 | 검색 아이콘 | 알림(뱃지) | 프로필 아바타

[히어로 섹션]
  지역 태그 (Atlanta · Suwanee)
  타이틀: "미국 한인 올인원 플랫폼"
  서브: 커뮤니티 · 라이드 · 게임 · 매칭
  검색바 (전체 검색)
  실시간 지도 미니뷰 (드라이버 핀 표시)
  [라이드 요청] [드라이버 등록] 버튼

[실시간 통계 4칸]
  82K 회원 | 47 드라이버 | 1.8K 채팅중 | 2,340 내포인트

[빠른 메뉴 아이콘 (가로 스크롤 8개)]
  커뮤니티 | 구인구직 | 중고장터 | 매칭
  노인알림 | 업소록 | 이벤트 | 포인트샵

[노인안심 배너 (강조띠)]
  초록 왼쪽 테두리 | 아이콘 | 설명 | [등록] 버튼

[Atlanta 단톡방 미리보기]
  온라인 인원수 | 최근 메시지 2개
  메시지 입력창 + 전송버튼

[최신 게시글]
  탭: 전체 / 자유 / Atlanta / 육아 / 이민 / 주식
  게시글 카드 3개 (태그 + 제목 + 조회/댓글)

[게임 & 포인트]
  내 포인트 표시 | 고스톱 / 포커 / 퀴즈 카드

[오늘의 매칭]
  매칭 프로필 아바타 미리보기 | [매칭 시작] 버튼
```

### 하단 탭바 (5탭 — iOS·Android 공통)
```
홈 | 커뮤니티 | 라이드 | 채팅 | 내 정보
(커뮤니티·채팅 탭에 빨간 뱃지 표시)
```

### FAB (플로팅 액션 버튼)
```
iOS     : 원형 FAB — [+] 아이콘 (우하단, 홈 인디케이터 위)
Android : Extended FAB — [+] 글쓰기 (텍스트 포함, 우하단)
```

---

## 19. iOS vs Android 플랫폼별 고려사항

### iOS 특이사항
```
UI 가이드    : Apple Human Interface Guidelines (HIG)
상단 노치    : Dynamic Island 대응 (iPhone 14 Pro+)
              Safe Area Top Inset 확보
하단 영역    : Home Indicator Safe Area 확보 필수
              FAB는 홈 인디케이터 위 배치
아이콘       : SF Symbols 활용 권장
햅틱         : Haptic Feedback (터치 진동) 적용
권한 팝업    : 위치·알림·카메라 각각 사용 목적 명시
              (거부 시 기능 설명 재유도)
배포         : App Store 심사 (평균 1~3일)
결제 주의    : 포인트 구매는 Apple IAP 통해야 함
              외부 결제 링크 금지 (정책 위반)
```

### Android 특이사항
```
UI 가이드    : Material Design 3 (Material You)
상단         : 상태바 아래 앱바 (노치 없는 기기도 대응)
하단 내비    : 제스처 내비게이션 or 3버튼 둘 다 대응
              Back 제스처 처리 필수 (스택 관리)
FAB          : Extended FAB (아이콘+텍스트) 권장
알림 권한    : Android 13+ 별도 알림 권한 팝업
배포         : Google Play Console (심사 보통 1~2일)
결제         : Google Play Billing API 필수
APK 직배포   : 가능 (초기 테스트용)
```

### 공통 주의사항
```
GPS 배터리   : 라이드 드라이버 모드 — 백그라운드 위치 권한 필요
              배터리 최적화 예외 처리 (Android)
              Background Location (iOS 항상허용)
WebSocket    : 앱 백그라운드 진입 시 연결 유지 전략 필요
              (Foreground Service — Android)
              (Background Task — iOS 제한적)
딥링크       : Universal Links (iOS) / App Links (Android)
              라이드 콜 수락, 채팅 알림 → 앱 특정 화면 이동
오프라인     : 기본 캐시 전략 (AsyncStorage)
앱 크기      : 초기 APK/IPA 50MB 이하 목표
              이미지 WebP 변환, 코드 스플리팅
```

---

## 20. 앱 화면 목록 (Screen List)

```
인증
  SplashScreen          로딩 + 자동 로그인 체크
  OnboardingScreen      첫 실행 소개 (3장 슬라이드)
  LoginScreen           이메일 + 소셜로그인 (Google/Apple)
  RegisterScreen        회원가입
  VerifyEmailScreen     이메일 인증 대기
  PhoneVerifyScreen     SMS 인증

홈
  HomeScreen            메인 홈 (와이어프레임 기준)
  SearchScreen          통합 검색 결과
  NotificationScreen    알림 목록

커뮤니티
  BoardListScreen       게시판 목록
  PostListScreen        게시글 목록
  PostDetailScreen      게시글 상세 + 댓글
  PostWriteScreen       글쓰기 에디터
  BlogScreen            개인 블로그

라이드
  RideHomeScreen        지도 + 드라이버 현황
  RideRequestScreen     출발지·목적지 입력
  RideWaitingScreen     드라이버 매칭 대기
  RideTrackingScreen    실시간 드라이버 추적
  RideCompleteScreen    완료 + 별점 평가
  DriverOnlineScreen    드라이버 — 콜 대기 지도
  DriverCallScreen      콜 수락/거절 팝업
  DriverNavigateScreen  목적지 내비게이션

게임
  GameLobbyScreen       게임 목록 + 내 포인트
  GoStopScreen          고스톱 (WebSocket 멀티플레이)
  PokerScreen           텍사스 홀덤
  QuizScreen            일일 퀴즈
  LeaderboardScreen     리더보드
  PointsScreen          포인트 내역 + 전환
  PointsShopScreen      포인트샵

매칭
  MatchIntroScreen      서비스 소개 + 인증 유도
  MatchVerifyScreen     신분증 업로드
  MatchProfileSetup     프로필 작성
  MatchBrowseScreen     카드 스와이프 (Tinder 스타일)
  MatchLikesScreen      받은/보낸 좋아요
  MatchChatScreen       매칭 1:1 채팅

노인알림
  ElderIntroScreen      서비스 소개
  ElderCheckinScreen    체크인 화면 (큰 UI)
  ElderSOSScreen        SOS 긴급 버튼
  GuardianSetupScreen   보호자 등록
  GuardianDashScreen    보호자 모니터링

채팅
  ChatListScreen        채팅방 목록
  ChatRoomScreen        채팅방 (WebSocket 실시간)
  DMScreen              1:1 다이렉트 메시지

내 정보
  ProfileScreen         내 프로필
  EditProfileScreen     프로필 수정
  SettingsScreen        앱 설정
  LanguageScreen        언어 선택 (KO/EN)
  NotifSettingScreen    알림 설정
  BillingScreen         결제 내역
  ElderModeScreen       노인 전용 모드 진입
```

---

## 21. 노인 전용 모드 (Elder Mode)

노인 사용자를 위한 별도 간소화 UI 모드

```
진입     : 설정 > "노인 모드 활성화" 또는 보호자가 원격 설정
글씨     : 전체 폰트 사이즈 +4px 확대 (최소 18px)
버튼     : 최소 터치 영역 60px × 60px
색상     : 고대비 모드 (배경 흰색, 텍스트 진한 검정)
홈 화면  : 3개 버튼만 표시
            [체크인 하기] [긴급 SOS] [가족과 통화]
SOS      : 홈 화면 하단 1/3 빨간 버튼
            3초 누르면 발동 + 진동 피드백
음성     : TTS 알림 읽어주기 옵션 (한국어)
```

---

## 22. 앱스토어 출시 준비 체크리스트

```
공통
  [ ] 앱 아이콘 (1024×1024 PNG, 각 해상도 대응)
  [ ] 스플래시 스크린 디자인
  [ ] 개인정보처리방침 URL (필수)
  [ ] 이용약관 URL (필수)
  [ ] 스크린샷 (iPhone / Android 각 5장 이상)
  [ ] 앱 설명문 (한국어 + 영어)
  [ ] 키워드 최적화 (ASO)

iOS (App Store)
  [ ] Apple Developer 계정 ($99/년)
  [ ] 프로비저닝 프로파일 + 인증서 설정
  [ ] App Store Connect 앱 등록
  [ ] TestFlight 베타 배포 (심사 전 테스트)
  [ ] 인앱결제 포인트 상품 등록 (Apple IAP)
  [ ] 위치·카메라·알림 권한 사용 목적 영문 기재
  [ ] Privacy Manifest 파일 (iOS 17+ 필수)

Android (Google Play)
  [ ] Google Play Console 계정 ($25 일회성)
  [ ] 키스토어 파일 안전 보관 (분실 시 업데이트 불가)
  [ ] AAB (Android App Bundle) 빌드
  [ ] 내부 테스트 → 비공개 테스트 → 프로덕션 순서 배포
  [ ] Google Play Billing 연동 확인
  [ ] 데이터 보안 섹션 작성 (Play Console)
  [ ] 타겟 API 레벨 최신 유지 (현재 API 35)
```

---

*본 문서는 Claude Code 작업 시 /CLAUDE.md 또는 프로젝트 루트에 배치하여 참조용으로 활용*  
*버전: v1.2 | 최종 수정: 2026-03-27*

---

## 23. 앱 내 음성·영상 통화 (WebRTC)

### 개요
```
Twilio 없이 앱 자체에서 카카오톡과 동일한 방식으로
회원 간 음성·영상 통화 구현
통화 연결 후 서버를 거치지 않는 P2P 직접 통신
→ 통화 비용 0원, 외부 서비스 불필요
```

### 통화 흐름
```
발신자                   시그널링 서버              수신자
  |                    (WebSocket 기존 활용)          |
  |── 통화 요청 ───────────────────────→              |
  |                           |── FCM 푸시 알림 ────→ |
  |                           |      "OOO님이 전화 중" |
  |                           |←── 수락 ──────────── |
  |←── 연결 정보 교환(SDP/ICE Candidate) ──────────→ |
  |                                                   |
  |◄══════ P2P 직접 음성/영상 통화 (서버 미경유) ════ |
```

### 필요 서버
```
시그널링 서버  기존 Ratchet WebSocket에 통화 채널 추가
               별도 서버 불필요

TURN 서버     P2P 직접 연결 불가 시(방화벽·NAT) 중계
               Coturn 오픈소스 → DigitalOcean Droplet 설치
               비용: 월 $6~12 (서버비만)
               또는 Cloudflare TURN → $0.05/GB (거의 무료)
```

### React Native 구현
```javascript
// react-native-webrtc 패키지 사용
import { RTCPeerConnection, RTCView, mediaDevices } from 'react-native-webrtc'

// 음성 통화
const stream = await mediaDevices.getUserMedia({ audio: true })

// 영상 통화
const stream = await mediaDevices.getUserMedia({ audio: true, video: true })
```

### 지원 기능
```
1:1 음성 통화   중간 난이도 / 무료
1:1 영상 통화   중간 난이도 / 무료
통화 중 채팅    쉬움 / 무료
그룹 통화(3명+) 어려움 / TURN 서버 트래픽 비용 발생
```

### 노인 알림 + WebRTC 연동
```
기존 (FCM만)
  FCM 푸시 → 보호자 알림 수신
  → 기기 기본 전화앱으로 별도 전화   ← 앱 밖으로 이탈

WebRTC 추가 후
  FCM 푸시 → 보호자 알림 수신
  → [앱 내 전화] 버튼 터치
  → 부모님 폰 수신 화면 즉시 표시    ← 앱 안에서 완결
  → 영상 통화로 얼굴 확인 가능
```

### WebSocket 채널 구조 추가
```
private-call.{userId}    — 통화 요청·수락·거절 시그널
private-call.{roomId}    — SDP / ICE Candidate 교환
```

---

## 24. 개발 순서 전체 확정 (최종)

### Phase 1 — MVP 코어 (주말 4~5회, 약 5주)
```
[ ] DigitalOcean 서버 세팅 (Nginx + PHP + MySQL + Redis)
[ ] Laravel 프로젝트 초기화 + 도메인 + SSL
[ ] 회원가입 / 로그인 / 이메일 인증
[ ] 기본 게시판 (자유 / 지역 / 카테고리별)
[ ] 구인구직 게시판
[ ] 중고장터
[ ] 한인 업소록 기본
[ ] 포인트 기본 (출석체크·게시글 적립)
[ ] 관리자 기본 대시보드
[ ] Vue.js 프론트 + 모바일 반응형
```

### Phase 2 — 실시간 + 안심 서비스 (주말 3~4회, 약 3주)
```
[ ] WebSocket 서버 구축 (Laravel Reverb)
[ ] 지역별·테마별 단톡방
[ ] 24시간 오픈채팅
[ ] 1:1 DM
[ ] 노인 안심 알림 (FCM + Laravel Scheduler)
[ ] 보호자 대시보드
[ ] WebRTC 음성 통화 (1:1)
[ ] WebRTC 영상 통화 (1:1)
[ ] TURN 서버 세팅 (Coturn)
[ ] 모바일 PWA 설치 지원
[ ] React Native 앱 기본 구조
```

### Phase 3 — React Native 앱 완성 (주말 3~4회, 약 3주)
```
[ ] iOS / Android 공통 화면 구현 (Screen List §20 전체)
[ ] FCM 푸시 알림 앱 연동
[ ] 노인 전용 모드 (Elder Mode)
[ ] GPS 위치 권한 처리
[ ] 딥링크 설정 (Universal Links / App Links)
[ ] TestFlight 베타 (iOS) / 내부 테스트 (Android)
[ ] 앱스토어 심사 제출
```

### Phase 4 — 게임 & 포인트 (주말 4~5회, 약 4주)
```
우선순위: 게임이 매칭·라이드보다 먼저

[ ] 일일 퀴즈 (가장 쉬움, 먼저 출시)
[ ] 포인트 → 캐시 전환 시스템
[ ] 포인트샵 (업소 쿠폰 교환)
[ ] 리더보드 (주간/월간)
[ ] 고스톱 WebSocket 멀티플레이
[ ] 텍사스 홀덤
[ ] 회원 등급 시스템 (씨앗→참나무)
```

### Phase 5 — 매칭 서비스 (주말 3~4회, 약 3주)
```
우선순위: 게임 다음, 라이드 이전

[ ] 신분증 업로드 인증 (Stripe Identity 또는 수동 검토)
[ ] AI 스캠 필터 (메시지 패턴 감지)
[ ] 연령대별 매칭 프로필
[ ] 카드 스와이프 UI (Tinder 스타일)
[ ] 매칭 1:1 채팅
[ ] 매칭 내 WebRTC 영상 통화 연동
[ ] 신고·블랙리스트 시스템
[ ] 프리미엄 매칭 (포인트 소모)
```

### Phase 6 — 알바 라이드 (주말 5~6회, 약 5주)
```
우선순위: 마지막 (가장 복잡)

[ ] Google Maps API 연동
[ ] 드라이버 등록·인증 (면허·차량)
[ ] 실시간 드라이버 위치 브로드캐스트 (WebSocket)
[ ] 콜 요청·수락·거절 플로우
[ ] 실시간 위치 추적 (승객 화면)
[ ] 내비게이션 연동 (Google Maps 앱 연동)
[ ] Stripe 결제 연동
[ ] 별점·리뷰 시스템
[ ] 드라이버 수입 정산 대시보드
[ ] 라이드 관리자 모니터링
```

### Phase 7 — 고도화 (지속)
```
[ ] AI 검색 (OpenAI 연동)
[ ] 그룹 WebRTC 통화 (3명+)
[ ] 음식 배달 연결
[ ] 라이브 방송
[ ] iOS / Android 네이티브 앱 고도화
[ ] 다국어 확장 (스페인어)
[ ] 추천 알고리즘
```

### 전체 타임라인 요약 (주말 하루 8시간 기준)
```
Phase 1   MVP 코어           5주   (약 40시간)
Phase 2   실시간 + 안심       3주   (약 24시간)
Phase 3   앱 완성 + 출시      3주   (약 24시간)
Phase 4   게임 & 포인트       4주   (약 32시간)
Phase 5   매칭 서비스         3주   (약 24시간)
Phase 6   알바 라이드         5주   (약 40시간)
─────────────────────────────────────
총합                         23주   (약 6개월)
```

---

## 25. Phase별 앱 화면 변경 계획

### 핵심 원칙
```
Phase 1 출시 시 라이드·게임·매칭 UI는 완전히 숨김
기능이 완성될 때마다 앱 업데이트로 자연스럽게 추가
처음부터 확장 가능한 구조로 코드 설계
```

---

### Phase 1 출시 버전 (라이드·게임·매칭 제외)

#### 히어로 섹션
```
[지도 없음] 심플 검색바만
  - 지역 태그 (Atlanta · Suwanee)
  - 타이틀: "미국 한인 커뮤니티"
  - 서브: 게시판 · 구인구직 · 채팅 · 업소록
  - 검색바
```

#### 실시간 통계 3칸
```
82K 회원 | 1.8K 채팅중 | 340 내 포인트
(드라이버 수 칸 없음)
```

#### 빠른 메뉴 아이콘 6개
```
커뮤니티 | 구인구직 | 중고장터
업소록 | 노인알림 | 이벤트
(라이드·게임·매칭 아이콘 없음)
```

#### 하단 탭바 5탭
```
홈 | 커뮤니티 | 채팅(뱃지) | 업소록 | 내 정보
(라이드 탭 없음)
```

#### 포인트 섹션
```
출석체크 (+10P) 버튼만
게임 카드 없음
```

#### FAB
```
iOS     : 원형 [+] 글쓰기
Android : 원형 [+] 글쓰기 (Extended 아님)
```

---

### Phase 2 추가 (단톡방·노인알림·WebRTC)
```
변경 없음 — 이미 Phase 1에 포함
단톡방·노인알림은 Phase 1부터 노출
WebRTC 통화 버튼 → DM 화면 내 [전화] 아이콘 추가
```

---

### Phase 4 추가 (게임 & 포인트)
```
빠른 메뉴  : 게임 아이콘 추가 → 7개
홈 하단    : 게임 & 포인트 섹션 추가
             고스톱 / 포커 / 퀴즈 카드
포인트 섹션: 출석체크 + 게임 입장 버튼
```

---

### Phase 5 추가 (매칭)
```
빠른 메뉴  : 매칭 아이콘 추가 → 8개
홈 하단    : 오늘의 매칭 섹션 추가
             프로필 아바타 미리보기 + [매칭 시작] 버튼
```

---

### Phase 6 추가 (알바 라이드) — 완성판
```
히어로     : 실시간 드라이버 지도 추가
             [라이드 요청] [드라이버 등록] 버튼
통계       : 드라이버 수 칸 추가 → 4칸
             82K 회원 | 47 드라이버 | 1.8K 채팅중 | 포인트
빠른 메뉴  : 라이드 아이콘 추가 (8개 유지, 순서 조정)
하단 탭바  : 라이드 탭 추가 → 5탭
             홈 | 커뮤니티 | 라이드 | 채팅 | 내 정보
FAB        : Android → Extended FAB (아이콘 + 글쓰기 텍스트)
```

---

### Phase별 탭바 변화 요약

```
Phase 1~3   홈 | 커뮤니티 | 채팅 | 업소록 | 내 정보   (4+1탭)
Phase 4~5   홈 | 커뮤니티 | 채팅 | 게임   | 내 정보   (게임 탭으로 교체)
Phase 6+    홈 | 커뮤니티 | 라이드| 채팅   | 내 정보   (라이드 탭 추가)
```

---

### 앱 버전 관리 계획
```
v1.0.0   Phase 1 출시  — 커뮤니티·구인구직·채팅·업소록·노인알림
v1.1.0   Phase 2 완료  — WebRTC 음성·영상 통화 추가
v1.2.0   Phase 3 완료  — 앱 안정화 + 앱스토어 정식 출시
v2.0.0   Phase 4 완료  — 게임 & 포인트 (메이저 업데이트)
v2.1.0   Phase 5 완료  — 매칭 서비스
v3.0.0   Phase 6 완료  — 알바 라이드 (메이저 업데이트)
```

---

## 26. 인프라 & 계정 정보 (확정)

```
서버 IP        : 68.183.60.70
서버 이름      : somekorean (DigitalOcean Droplet)
서버 OS        : Ubuntu 24.04 LTS / NYC3
서버 플랜      : 1GB RAM / 25GB SSD / $6/월
도메인         : somekorean.com (GoDaddy 구매)
DNS            : DigitalOcean Nameserver 연결 완료
GitHub 저장소  : github.com/romance76/somekorean (Private)
```

---

## 27. GitHub + Claude Code + 서버 자동 배포 설정

### 전체 흐름
```
Claude Code (Windows PC)
        ↓ 코드 작성 + git push
   GitHub (romance76/somekorean)
        ↓ webhook 또는 서버 자동 pull
  DigitalOcean (68.183.60.70)
   somekorean.com 자동 반영
```

### Claude Code가 자동으로 해줄 것
```
1. 코드 작성 및 수정
2. git add, commit, push (GitHub으로 자동 업로드)
3. SSH로 서버 접속
4. git pull (서버에 최신 코드 자동 반영)
5. php artisan migrate (DB 변경사항 적용)
6. npm run build (프론트엔드 빌드)
7. 서버 재시작 (필요 시)
```

### 1단계 — Windows에서 Git 초기 설정
```bash
# Claude Code가 자동으로 실행
git config --global user.name "romance76"
git config --global user.email "your@email.com"
git clone https://github.com/romance76/somekorean.git
cd somekorean
```

### 2단계 — 서버에 SSH 키 설정
```bash
# Claude Code가 자동으로 처리
# Windows에서 SSH 키 생성
ssh-keygen -t rsa -b 4096 -C "somekorean-deploy"

# 공개키를 서버에 등록
ssh-copy-id root@68.183.60.70

# 이후 비밀번호 없이 자동 접속 가능
ssh root@68.183.60.70
```

### 3단계 — 서버에 자동 배포 스크립트 설치
```bash
# /var/www/somekorean/deploy.sh
#!/bin/bash
cd /var/www/somekorean
git pull origin main
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan config:cache
php artisan route:cache
npm install
npm run build
sudo systemctl reload nginx
sudo supervisorctl restart reverb
echo "✅ 배포 완료 $(date)"
```

### 4단계 — GitHub Webhook 자동 배포 (선택)
```
GitHub → somekorean 저장소
→ Settings → Webhooks → Add webhook
→ Payload URL: http://68.183.60.70/webhook.php
→ Content type: application/json
→ Events: push (main 브랜치)

서버에서 push 감지 → deploy.sh 자동 실행
→ 코드 수정 후 git push 한 번으로 서버 자동 반영
```

### Claude Code 시작 명령어
```
집에서 Claude Code 열고 이렇게 말하면 돼요:

"KoreanCommunity_ProjectSpec_v1.md 파일을 참고해서
아래 정보로 Phase 1 서버 세팅 시작해줘:

서버 IP    : 68.183.60.70
도메인     : somekorean.com
GitHub     : github.com/romance76/somekorean
서버 비밀번호: (아까 만든 비밀번호)

GitHub 연동하고 코드 push하면 서버에 자동 배포되도록
전체 설정해줘"
```

### 자동 배포 완성 후 작업 순서
```
Claude Code가 코드 수정
    ↓
git push → GitHub 자동 업로드
    ↓
서버 webhook 감지
    ↓
deploy.sh 자동 실행
    ↓
somekorean.com 자동 반영
(사람이 할 일 없음)
```

### GitHub 저장소 설정 확인
```
저장소     : romance76/somekorean
공개여부   : Private ✅
브랜치     : main (기본)
.gitignore : Laravel (설정 필요)
README     : On
```

### .gitignore 필수 항목 (Laravel)
```
/vendor
/node_modules
.env                ← 절대 GitHub에 올리면 안됨 (비밀번호 포함)
.env.backup
/public/hot
/public/storage
/storage/*.key
.phpunit.result.cache
```

### 주의사항
```
⚠️ .env 파일은 절대 GitHub에 올리면 안됨
   → API 키, DB 비밀번호 노출 위험
   → 서버에 직접 업로드해야 함

⚠️ 서버 비밀번호는 따로 안전하게 보관
   → 비밀번호 분실 시 서버 접속 불가

⚠️ GitHub 토큰(Personal Access Token) 필요
   → github.com → Settings → Developer settings
   → Personal access tokens → Generate new token
   → Claude Code에 제공하면 자동으로 push 가능
```
