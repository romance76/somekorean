# SomeKorean - 미국 한인 커뮤니티 통합 플랫폼

## 프로젝트 개요
- **사이트**: https://somekorean.com
- **서버**: DigitalOcean (68.183.60.70), Ubuntu
- **GitHub**: https://github.com/romance76/somekorean
- **자동 배포**: GitHub push → Webhook → deploy.sh 자동 실행

## 기술 스택
| 구분 | 기술 |
|------|------|
| Backend | Laravel (PHP 8.2) |
| Frontend | Vue 3 (Composition API) + Vite |
| CSS | Tailwind CSS |
| DB | MySQL |
| 실시간 | Laravel Reverb (WebSocket) + Socket.io |
| 서버 | Nginx + PHP-FPM |
| 배포 | GitHub Webhook → deploy.sh |

## 프로젝트 규모
| 항목 | 수량 |
|------|------|
| API 라우트 | 461개 |
| Vue 페이지 | 166개 |
| API 컨트롤러 | 56개 |
| Eloquent 모델 | 68개 |
| DB 마이그레이션 | 53개 |

## 주요 기능 목록

### 커뮤니티
- **게시판**: 자유게시판, 지역별 게시판, 카테고리별 분류
- **Q&A**: 질문/답변, 카테고리별 분류, 채택 기능
- **동호회**: 생성/가입/탈퇴, 승인제, 게시판, 회원관리, 방장/운영자 권한
- **댓글/대댓글**: 좋아요, 알림 발송

### 생활정보
- **구인구직**: 공고 등록/수정/삭제, 지원하기, 관리자 권한
- **중고장터**: 매물 등록, 이미지 업로드, 판매완료 처리
- **부동산**: 매물 등록, 지도 연동, 카테고리 분류
- **업소록**: 업소 등록, 리뷰/평점, 카테고리/지역 필터

### 콘텐츠
- **뉴스**: 자동 크롤링 + 수동 등록, 카테고리별 분류
- **레시피**: 레시피 등록, 재료/단계별 작성, 카테고리 분류
- **이벤트**: 이벤트 등록, 참가 신청, 일정 관리
- **숏츠**: 짧은 영상 콘텐츠, 스와이프 UI

### 쇼핑/거래
- **쇼핑정보**: 딜/쿠폰/스토어 정보 관리
- **공동구매**: 공동구매 모집/참여

### 소통
- **채팅**: 1:1 및 그룹 채팅, 실시간 WebSocket, 방장 관리 (이름수정/삭제)
- **알림**: 좋아요/댓글/답글/채팅 실시간 알림
- **멘토링**: 멘토-멘티 매칭

### 게임/포인트
- **고스톱**: 실시간 멀티플레이어 + 솔로 모드
- **포인트샵**: 포인트 적립/사용, 출석체크
- **퀴즈**: 퀴즈 게임

### 어르신 안심서비스
- **체크인**: 일일 안부 확인
- **보호자 대시보드**: 어르신 상태 모니터링
- **자동 알림**: 미체크인 시 보호자 알림

### 기타
- **알바라이드**: 카풀/라이드 매칭
- **음악듣기**: 음악 플레이어
- **AI검색**: AI 기반 검색
- **친구**: 친구 추가/관리

### 관리자
- **사이트 설정**: 메뉴 순서/표시 관리 (SiteSettings → NavBar 자동 반영)
- **회원 관리**: 회원 목록, 권한 관리
- **콘텐츠 관리**: 게시글/댓글 관리
- **통계 대시보드**: 방문자, 게시글, 회원 통계

## 배포 방법

### 자동 배포 (권장)
1. 로컬에서 코드 수정
2. `git add . && git commit -m "메시지" && git push origin main`
3. GitHub Webhook이 서버의 `deploy-webhook.php` 호출
4. `deploy.sh` 자동 실행 (git pull → composer → npm build → migrate → cache)

### 수동 배포
```bash
ssh root@68.183.60.70
cd /var/www/somekorean
bash deploy.sh
```

## 서버 접속 정보
```
SSH: ssh root@68.183.60.70
웹서버: Nginx
PHP: 8.2-FPM
DB: MySQL
프로젝트 경로: /var/www/somekorean
로그: /var/www/somekorean/storage/logs/
```

## 개발 규칙
1. **프론트엔드 + 백엔드 동시 수정** - 한쪽만 수정하면 안 됨
2. **새 메뉴 추가 시**: NavBar allNavItems + SiteSettings allMenuDefs + 라우터 3곳 동시 추가
3. **DB 테이블 변경 시**: 마이그레이션 + 모델 + 컨트롤러 + Vue 전부 동시 수정
4. 메뉴 순서/표시는 관리자 SiteSettings에서 설정 → site store → NavBar에 자동 반영

## 최근 업데이트 이력 (Phase 8 - 2026-03-31)
- ClubDetail fetchClub 데이터 바인딩 수정 (동호회 이름/설명 표시)
- 좋아요/댓글/답글 알림 발송 시스템
- 채팅방 방장 관리 (삭제/이름수정 API+Vue UI)
- 전체 권한 체크 완비 (Job/Market/Event/Recipe/Club Controller)
- RecipeDetail + RealEstateDetail 수정/삭제 버튼 추가
- 쇼핑/뉴스/업소록/게임/숏츠 전면 개선
- 어르신 안심서비스 대폭 확장
- GitHub 연동 + 자동 배포 Webhook 설정
