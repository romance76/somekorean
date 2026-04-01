#!/bin/bash
# SomeKorean - 빌드 에러 수정 + DB 세팅 + 전체 배포 스크립트
# 서버에서 실행: bash fix_build.sh

APP_DIR="/var/www/somekorean"
DB_NAME="somekorean"
DB_USER="somekorean_user"
DB_PASS="your_db_password"  # .env 에서 확인 후 변경

echo "=== [1/5] tailwindcss 패키지 재설치 ==="
cd $APP_DIR
npm install tailwindcss @tailwindcss/vite --save-dev

echo "=== [2/5] npm run build ==="
npm run build
if [ $? -ne 0 ]; then
  echo "빌드 실패! 에러 확인 필요"
  exit 1
fi
echo "빌드 성공!"

echo "=== [3/5] DB 스키마 생성 (테이블이 없으면 생성) ==="
mysql -u $DB_USER -p$DB_PASS $DB_NAME < $APP_DIR/database/schema.sql
echo "스키마 완료"

echo "=== [4/5] 기본 데이터 삽입 (게시판 + 관리자) ==="
mysql -u $DB_USER -p$DB_PASS $DB_NAME < $APP_DIR/database/seed.sql
echo "시드 완료"

echo "=== [5/5] Laravel 캐시 클리어 ==="
php8.2 artisan config:clear
php8.2 artisan route:clear
php8.2 artisan cache:clear
php8.2 artisan storage:link

echo "=== 완료! ==="
echo "관리자 계정: admin@somekorean.com / Admin1234!"
