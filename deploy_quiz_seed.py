import paramiko
import sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
DB_USER = 'somekorean_user'
DB_PASS = 'SK_DB@2026!secure'
DB_NAME = 'somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:100]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

print('\n=== Quiz Questions Seed ===')

# Write PHP script via sftp binary mode to handle Korean UTF-8
php = '''<?php
$pdo = new PDO("mysql:host=127.0.0.1;dbname=somekorean;charset=utf8mb4", "somekorean_user", "SK_DB@2026!secure");
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Check existing count
$existing = $pdo->query("SELECT COUNT(*) FROM quiz_questions")->fetchColumn();
echo "Existing quiz questions: $existing\\n";

$questions = [
  // === 문화 (culture) ===
  ["culture", "한국의 전통 명절 중 음력 1월 1일에 지내는 명절은?",
   "추석", "설날", "단오", "한식", "B",
   "설날은 음력 1월 1일로, 한국의 최대 명절 중 하나입니다. 차례를 지내고 세배를 드리며 떡국을 먹습니다."],

  ["culture", "한국에서 결혼식 후 신랑 신부가 함께 하는 전통 의식은?",
   "돌잔치", "폐백", "회갑", "제사", "B",
   "폐백은 신부가 시댁 어른들에게 처음 인사를 드리는 전통 혼례 의식입니다."],

  ["culture", "한국의 전통 발효 음식으로 배추, 무, 고추가루 등으로 만드는 것은?",
   "된장", "간장", "김치", "고추장", "C",
   "김치는 채소를 소금에 절이고 양념하여 발효시킨 한국의 대표 전통 음식입니다."],

  ["culture", "한국에서 나이 한 살을 더 먹는 전통적인 날은?",
   "생일", "설날", "추석", "동지", "B",
   "한국의 전통 나이 계산법(세는 나이)에서는 설날에 모두가 한 살씩 더 먹습니다."],

  ["culture", "한국의 전통 타악기로 농악에서 주로 사용되는 꽹과리와 함께 쓰이는 악기는?",
   "가야금", "장구", "해금", "피리", "B",
   "장구는 한국 전통 타악기로 모양이 허리가 잘록한 북 형태이며 농악, 판소리 등에 사용됩니다."],

  ["culture", "한국에서 아이의 첫 번째 생일을 축하하는 행사를 무엇이라 하나요?",
   "환갑", "돌잔치", "칠순", "백일잔치", "B",
   "돌잔치는 아기의 첫 번째 생일(돌)을 축하하는 잔치로, 돌잡이를 통해 아이의 미래를 점칩니다."],

  ["culture", "추석에 먹는 전통 음식으로 쌀가루를 빚어 솔잎 위에 찐 것은?",
   "인절미", "약식", "송편", "식혜", "C",
   "송편은 추석에 먹는 대표적인 전통 떡으로, 솔잎(송엽) 위에 찐다고 해서 송편이라 합니다."],

  ["culture", "한국의 전통 옷으로 명절이나 특별한 날에 입는 의복은?",
   "기모노", "치파오", "한복", "아오자이", "C",
   "한복은 한국의 전통 의복으로 저고리, 치마(여성) 또는 바지(남성)로 구성됩니다."],

  ["culture", "한국에서 어른에게 두 손으로 물건을 드리거나 받는 이유는?",
   "빠르게 전달하기 위해", "예의와 존경을 표현하기 위해", "물건을 안 떨어뜨리기 위해", "규칙이기 때문에", "B",
   "두 손으로 주고받는 것은 한국의 예절 문화로, 상대방에 대한 존경과 배려를 표현합니다."],

  ["culture", "한국의 전통 가옥 형태로 바닥에 온돌(구들)을 깔아 따뜻하게 하는 집은?",
   "한옥", "초가집", "기와집", "귀틀집", "A",
   "한옥은 한국의 전통 건축 양식으로, 온돌 난방, 마루, 기와 또는 초가지붕이 특징입니다."],

  // === 역사 (history) ===
  ["history", "한국의 훈민정음(한글)을 창제한 조선의 왕은?",
   "태조", "세종대왕", "태종", "성종", "B",
   "세종대왕은 1443년 한글(훈민정음)을 창제하여 백성들이 쉽게 글을 읽고 쓸 수 있도록 했습니다."],

  ["history", "한국이 일본으로부터 광복을 맞은 날짜는?",
   "3월 1일", "8월 15일", "7월 4일", "10월 3일", "B",
   "1945년 8월 15일, 한국은 36년간의 일본 식민지배에서 해방되었습니다. 이날을 광복절이라 합니다."],

  ["history", "한국의 삼국시대를 이루었던 세 나라가 아닌 것은?",
   "고구려", "백제", "신라", "가야", "D",
   "삼국시대의 세 나라는 고구려, 백제, 신라입니다. 가야는 삼국과 같은 시기에 존재했지만 삼국에 포함되지 않습니다."],

  ["history", "한국 역사에서 고려 시대에 몽골의 침략에 맞서 만든 것은?",
   "경복궁", "팔만대장경", "첨성대", "석굴암", "B",
   "팔만대장경(고려대장경)은 몽골 침략을 부처의 힘으로 물리치기 위해 약 16년에 걸쳐 제작되었습니다."],

  ["history", "대한민국 정부가 수립된 해는?",
   "1945년", "1950년", "1948년", "1953년", "C",
   "대한민국 정부는 1948년 8월 15일 수립되었으며, 이승만이 초대 대통령이 되었습니다."],

  // === 언어 (language) ===
  ["language", "한글에서 받침(종성)으로만 쓰이지 않는 자음은?",
   "ㄱ", "ㅎ", "ㄷ", "ㅇ", "D",
   "ㅇ은 초성에서는 소리가 없는 자음으로 쓰이지만, 종성(받침)에서는 \'ng\' 소리를 냅니다."],

  ["language", "영어 'I miss you'를 한국어로 자연스럽게 표현하면?",
   "나는 너를 미스해", "보고 싶어", "나는 너가 없어", "너를 그리워해", "B",
   "'보고 싶어'는 영어 'I miss you'에 해당하는 한국어 표현입니다."],

  ["language", "한국어에서 존댓말로 올바른 표현은?",
   "밥 먹어", "밥 드세요", "밥 먹어요", "밥 먹어라", "B",
   "'드세요'는 '먹다'의 높임말로, 어른이나 손님에게 사용하는 정중한 표현입니다."],

  ["language", "한국어 수사에서 '하나, 둘, 셋, 넷...'과 다른 계통의 숫자는?",
   "다섯", "일, 이, 삼, 사...", "여섯", "일곱", "B",
   "한국어에는 순우리말 수사(하나, 둘, 셋...)와 한자어 수사(일, 이, 삼...)의 두 계통이 있습니다."],

  ["language", "미국에서 한국어로 전화할 때 사용하는 일반적인 인사말은?",
   "안녕하세요", "여보세요", "반갑습니다", "처음 뵙겠습니다", "B",
   "'여보세요'는 전화를 받거나 걸 때 사용하는 한국어 인사말입니다."],

  // === 미국 생활 (general) ===
  ["general", "미국에서 팁(Tip) 문화가 적용되지 않는 경우는?",
   "레스토랑", "택시/우버", "마트 계산원", "헤어살롱", "C",
   "미국 마트(슈퍼마켓) 계산원에게는 일반적으로 팁을 주지 않습니다. 팁 문화는 서비스업 중심입니다."],

  ["general", "미국의 사회보장번호(SSN)는 몇 자리로 구성되나요?",
   "7자리", "8자리", "9자리", "10자리", "C",
   "미국 사회보장번호(Social Security Number)는 XXX-XX-XXXX 형식의 9자리 숫자입니다."],

  ["general", "미국에서 의료보험 없이 응급실을 방문할 때 주로 발생하는 문제는?",
   "거부당한다", "막대한 의료비 청구", "무료로 치료받는다", "보험사가 대신 낸다", "B",
   "미국은 의료비가 매우 비싸며, 보험 없이 응급실을 방문하면 수천~수만 달러의 청구서가 나올 수 있습니다."],

  ["general", "미국에서 신용점수(Credit Score)를 높이는 방법으로 옳은 것은?",
   "신용카드를 여러 개 만든다", "카드 한도를 최대한 사용한다", "매달 카드 대금을 전액 납부한다", "현금만 사용한다", "C",
   "신용카드를 제때 전액 납부하는 것이 신용점수를 높이는 가장 효과적인 방법입니다."],

  ["general", "미국에서 운전면허증을 발급받는 기관은?",
   "FBI", "DMV (차량국)", "IRS (국세청)", "INS (이민국)", "B",
   "DMV(Department of Motor Vehicles)는 미국 각 주에서 운전면허증과 차량 등록을 담당하는 기관입니다."],

  ["general", "미국 세금 신고(Tax Return) 마감일은 일반적으로 언제인가요?",
   "1월 31일", "3월 15일", "4월 15일", "6월 30일", "C",
   "미국 연방 세금 신고 마감일은 매년 4월 15일입니다. 연장 신청 시 10월 15일까지 가능합니다."],

  ["general", "미국에서 '한인타운(Koreatown)'이 가장 큰 도시는?",
   "뉴욕", "로스앤젤레스", "시카고", "애틀랜타", "B",
   "LA 한인타운은 미국에서 가장 크고 활성화된 한인 밀집 지역으로, 약 10만 명의 한인이 거주합니다."],

  ["general", "미국의 의료보험 오픈 엔롤먼트(Open Enrollment) 기간은 일반적으로 언제인가요?",
   "1월~3월", "4월~6월", "11월~1월", "7월~9월", "C",
   "미국 건강보험 마켓플레이스 오픈 엔롤먼트는 보통 11월 1일에 시작하여 1월 15일에 종료됩니다."],

  ["general", "미국에서 한국 식재료를 구매하기 가장 좋은 곳은?",
   "월마트", "코스트코", "H마트(한국계 슈퍼마켓)", "트레이더조", "C",
   "H마트는 미국 최대 한국계 슈퍼마켓 체인으로 한국 식재료, 라면, 반찬 등을 가장 다양하게 판매합니다."],

  ["general", "미국에서 집을 임대할 때 일반적으로 필요한 보증금(Security Deposit)은?",
   "월세의 1개월치", "월세의 1~2개월치", "월세의 6개월치", "필요 없음", "B",
   "미국에서는 보통 월세 1~2개월치를 보증금으로 납부하며, 이사 후 손상이 없으면 반환받습니다."],
];

$stmt = $pdo->prepare("INSERT INTO quiz_questions
  (category, question, option_a, option_b, option_c, option_d, correct_answer, points, explanation, is_active, created_at, updated_at)
  VALUES (?, ?, ?, ?, ?, ?, ?, 20, ?, 1, NOW(), NOW())");

$count = 0;
foreach ($questions as $q) {
  $stmt->execute([$q[0], $q[1], $q[2], $q[3], $q[4], $q[5], $q[6], $q[7]]);
  $count++;
}

$total = $pdo->query("SELECT COUNT(*) FROM quiz_questions")->fetchColumn();
echo "Inserted: $count questions\\nTotal quiz_questions: $total\\n";
'''

print('\n[1] Writing quiz seed PHP...')
with sftp.open('/tmp/quiz_seed.php', 'wb') as f:
    f.write(php.encode('utf-8'))

print('\n[2] Running quiz seed...')
run(f'php8.2 /tmp/quiz_seed.php 2>&1', timeout=60)

print('\n[3] Checking counts...')
run(f"""mysql -u{DB_USER} -p'{DB_PASS}' {DB_NAME} -e "
SELECT 'quiz_questions' AS tbl, COUNT(*) AS cnt FROM quiz_questions
UNION SELECT 'match_profiles', COUNT(*) FROM match_profiles
UNION SELECT 'events', COUNT(*) FROM events
UNION SELECT 'posts', COUNT(*) FROM posts
UNION SELECT 'chat_rooms', COUNT(*) FROM chat_rooms;" 2>/dev/null""")

sftp.close()
client.close()
print('\n=== DONE ===')
