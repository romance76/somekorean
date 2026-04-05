# SomeKorean 프로젝트 진행 현황
> 마지막 업데이트: 2026-03-28

---

## 인프라 정보

| 항목 | 값 |
|------|-----|
| 도메인 | https://somekorean.com |
| 서버 IP | 68.183.60.70 (DigitalOcean) |
| GitHub | github.com/romance76/somekorean |
| 서버 경로 | /var/www/somekorean |
| DB | MySQL 8 / somekorean_user / SK_DB@2026!secure |
| SSL | Let's Encrypt (만료: 2026-06-25, 자동갱신) |

## 관리자 계정

| 항목 | 값 |
|------|-----|
| 이메일 | admin@somekorean.com |
| 비밀번호 | Admin1234! |

---

## 기술 스택

- **Backend**: Laravel 11, PHP 8.2, MySQL 8
- **Frontend**: Vue 3 (Composition API), Vite, Tailwind CSS v3
- **WebSocket**: Laravel Reverb (port 8080, Supervisor 관리)
- **Queue Worker**: somekorean-worker (Supervisor)
- **프로세스 관리**: Supervisor (`reverb` + `somekorean-worker` — 두 서비스 RUNNING)
- **웹서버**: Nginx + PHP-FPM 8.2

---

## CI/CD (GitHub Actions 자동 배포)

### 방식
`main` 브랜치에 push → GitHub Actions 자동 트리거

### 파이프라인 순서
1. `ubuntu-latest`에서 `npm ci` + `npm run build` (Vue3 프론트 빌드)
2. SCP로 `public/build/` 빌드 결과물 서버 전송
3. 서버 SSH 접속:
   - `git pull origin main`
   - `composer install --no-dev`
   - `php8.2 artisan migrate --force`
   - config/route/view 캐시
   - `php8.2-fpm` restart

### GitHub Secrets (설정 완료)
| Secret | 설명 |
|--------|------|
| `SERVER_HOST` | 68.183.60.70 |
| `SERVER_USER` | root |
| `SSH_PRIVATE_KEY` | ED25519 배포 전용 키 |

### 최근 Actions 실행 결과
| Run | Commit | 결과 |
|-----|--------|------|
| #3 | fe485f7 | ✅ success |
| #2 | 0c63f47 | ✅ success |
| #1 | 68ed6b9 | ❌ failure (Secrets 미설정 시절) |

---

## Phase 별 완료 현황

### Phase 1 — MVP ✅ 완료 (2026-03-27)

**Backend (Controllers)**
- AuthController — 회원가입, 로그인, 이메일 인증, JWT
- PostController — 게시글 CRUD, 좋아요
- BoardController — 게시판 목록 (15개 seeded)
- CommentController — 댓글/대댓글
- JobController — 구인구직 CRUD
- MarketController — 중고 장터 CRUD
- BusinessController — 한인 업소록 CRUD + 리뷰
- PointController — 포인트 적립/차감/전환
- MessageController — 1:1 쪽지
- AdminController — 관리자 대시보드
- ProfileController — 프로필 조회/수정
- SearchController — 통합 검색
- ReportController — 신고 처리

**DB 테이블 (22개)**
users, posts, boards, comments, job_posts, market_items, businesses, business_reviews, messages, point_logs, checkins, bookmarks, post_likes, reports + 기타

**Frontend Vue 페이지 (24개)**
Home, Login, Register, BoardList, PostList, PostDetail, PostWrite, JobList, JobDetail, JobWrite, MarketList, MarketDetail, MarketWrite, BusinessList, BusinessDetail, BusinessRegister, PointDashboard, MessageInbox, Dashboard(Admin), UserProfile, NavBar, BottomNav, NotFound, Search

---

### Phase 2 — 실시간 채팅 + 노인 서비스 + 퀴즈 ✅ 완료 (2026-03-27)

**채팅 시스템**
- chat_rooms, chat_messages 테이블
- ChatController, ChatRoom/ChatMessage 모델
- MessageSent 브로드캐스트 이벤트
- Laravel Reverb WebSocket 서버 (port 8080, Supervisor)
- Vue: ChatRooms.vue, ChatRoom.vue
- 채팅방 시드: 지역별 7개 + 테마 8개

**노인 안심 서비스**
- elder_settings 테이블
- ElderController, ElderSetting 모델
- ElderCheckCommand (cron: 매 시간) — 미응답 시 보호자 알림
- Vue: ElderHome.vue, ElderCheckin.vue (SOS 버튼), GuardianDashboard.vue

**일일 퀴즈**
- quiz_questions, quiz_attempts 테이블
- QuizController, 퀴즈 10개 seeded
- Vue: QuizGame.vue (/games/quiz)

---

### Phase 3 — 라이드 서비스 ✅ 완료 (2026-03-27)

**Backend**
- rides, driver_profiles, ride_reviews 테이블
- RideController — 요청/수락/취소/완료
- DriverController — 드라이버 등록, 온라인/오프라인, 위치 업데이트

**Frontend**
- RideMain.vue — 지도 + 드라이버 현황
- RideRequest.vue — 라이드 요청
- RideHistory.vue — 이용 내역
- DriverRegister.vue — 드라이버 등록
- DriverDashboard.vue — 수입/콜 현황

---

### Phase 4 — 게임 & 매칭 ✅ 완료 (2026-03-27~28)

**게임 (Vue 페이지)**
- GameLobby.vue — 게임 로비
- GoStop.vue — 고스톱 (멀티플레이)
- GoStopSolo.vue — 고스톱 솔로
- Poker.vue — 텍사스 홀덤
- HoldemSolo.vue — 홀덤 솔로
- OmokGame.vue — 오목
- Blackjack.vue — 블랙잭
- BingoGame.vue — 빙고
- Game2048.vue — 2048
- MemoryGame.vue — 메모리 게임
- QuizGame.vue — 일일 퀴즈 (Phase 2에 포함)
- Leaderboard.vue — 리더보드
- PointShop.vue — 포인트샵

**매칭**
- match_profiles, match_verifications 테이블
- MatchController — 프로필 등록, 브라우징, 좋아요/매칭
- MatchHome.vue, MatchBrowse.vue, MatchProfileSetup.vue

---

### 추가 구현 기능 (Phase 2~4 병행)

**뉴스**
- news 테이블, NewsController
- FetchNews artisan command (RSS 수집)
- NewsList.vue, NewsDetail.vue
- 샘플 뉴스 seeded

**이벤트 & 모임**
- events 테이블, EventController
- SeedEvents artisan command
- 이벤트 데이터 seeded

**친구 / 클럽**
- FriendController, ClubController
- friends, clubs 관련 테이블

**알림**
- NotificationController
- Notifications.vue

**포인트 룰 안내**
- PointRules.vue

---

## 현재 서버 파일 구조 (요약)

```
/var/www/somekorean/
├── app/
│   ├── Console/Commands/         (ElderCheck, FetchNews, SeedEvents, SeedRecentNews)
│   ├── Events/                   (MessageSent, GameStateChanged)
│   ├── Http/Controllers/API/     (26개 Controller)
│   └── Models/                   (20개+ Model)
├── database/migrations/          (22개+ 마이그레이션)
├── resources/js/
│   ├── pages/                    (50개+ Vue 페이지)
│   └── router/index.js
├── routes/api.php                (100개+ API 엔드포인트)
├── .github/workflows/deploy.yml  (자동 배포)
├── deploy.sh                     (수동 배포 스크립트)
└── public/build/                 (Vite 빌드 결과)
```

---

## 남은 작업 (Phase 5)

스펙 문서 기준 미구현 항목:

- [ ] Twilio SMS 연동 (노인 체크인 미응답 시 자동 문자/전화)
- [ ] Firebase FCM 푸시 알림
- [ ] Google Maps API 연동 (라이드 실제 지도)
- [ ] Stripe 결제 연동
- [ ] 매칭 신분증 인증 (Stripe Identity)
- [ ] AI 스캠 필터 (Google Vision API)
- [ ] PWA manifest + Service Worker
- [ ] 다국어 (Vue i18n 한/영)
- [ ] 관리자 IP 화이트리스트
- [ ] 에러 로그 Slack 알림

---

## 배포 방법 (현재)

### 자동 배포 (권장)
```bash
# 로컬에서 작업 후
git add -A
git commit -m "feat: 변경 내용"
git push origin main
# → GitHub Actions 자동 실행 (~5분 후 배포 완료)
```

### 수동 배포 (서버 직접)
```bash
ssh root@68.183.60.70
cd /var/www/somekorean
bash deploy.sh
```

### Python 스크립트 (로컬)
```bash
# C:\Users\Admin\Desktop\somekorean\deploy_*.py 파일들
python deploy.py          # 기본 배포
python deploy_mega.py     # Vue 전체 재업로드 + 빌드
```

---

## GitHub 커밋 히스토리

| Hash | 메시지 |
|------|--------|
| fe485f7 | ci: optimize deploy - build on Actions, SCP to server |
| 0c63f47 | feat: Phase 1-4 complete - Games, Match, Ride, News, Events, Elder, Chat |
| 68ed6b9 | ci: GitHub Actions auto-deploy + deploy script |
| 61a5d0e | feat: Phase 1 MVP - Laravel11 + Vue3 + MySQL |
