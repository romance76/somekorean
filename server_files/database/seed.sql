-- SomeKorean Seed Data
-- 기본 게시판 + 관리자 계정 생성

-- 기본 게시판 (boards)
INSERT IGNORE INTO `boards` (`name`, `slug`, `description`, `category`, `icon`, `sort_order`, `is_active`, `created_at`, `updated_at`) VALUES
('자유게시판',   'free',        '자유롭게 이야기해요',           'community', '💬', 1,  1, NOW(), NOW()),
('육아',         'parenting',   '육아 정보와 경험을 나눠요',     'community', '👶', 2,  1, NOW(), NOW()),
('뷰티/패션',   'beauty',      '뷰티와 패션 이야기',            'community', '💄', 3,  1, NOW(), NOW()),
('건강/의료',   'health',      '건강과 의료 정보',              'community', '🏥', 4,  1, NOW(), NOW()),
('여행',         'travel',      '여행 정보와 후기',              'community', '✈️', 5,  1, NOW(), NOW()),
('음식/레시피', 'food',        '맛있는 음식과 레시피',          'community', '🍳', 6,  1, NOW(), NOW()),
('교육/유학',   'education',   '교육과 유학 정보',              'community', '📚', 7,  1, NOW(), NOW()),
('이민/정착',   'immigration', '이민 생활 정보',                'community', '🏠', 8,  1, NOW(), NOW()),
('재정/투자',   'finance',     '재정 관리와 투자 이야기',       'community', '💰', 9,  1, NOW(), NOW()),
('취업이야기',  'jobs-talk',   '취업 경험과 이야기',            'community', '💼', 10, 1, NOW(), NOW()),
('Atlanta',      'atlanta',     'Atlanta 한인 게시판',           'local',     '🍑', 11, 1, NOW(), NOW()),
('Suwanee',      'suwanee',     'Suwanee 한인 게시판',           'local',     '📍', 12, 1, NOW(), NOW()),
('Johns Creek',  'johns-creek', 'Johns Creek 한인 게시판',       'local',     '📍', 13, 1, NOW(), NOW()),
('New York',     'new-york',    'New York 한인 게시판',          'local',     '🗽', 14, 1, NOW(), NOW()),
('Los Angeles',  'los-angeles', 'Los Angeles 한인 게시판',       'local',     '🌴', 15, 1, NOW(), NOW()),
('Dallas',       'dallas',      'Dallas 한인 게시판',            'local',     '🤠', 16, 1, NOW(), NOW()),
('Chicago',      'chicago',     'Chicago 한인 게시판',           'local',     '🌆', 17, 1, NOW(), NOW()),
('전문가칼럼',  'expert-column','전문가 칼럼 (이민/법률/의료)', 'expert',    '🎓', 18, 1, NOW(), NOW());

-- 기본 관리자 계정 (비밀번호: Admin1234!)
-- bcrypt hash of "Admin1234!"
INSERT IGNORE INTO `users` (`name`, `username`, `email`, `password`, `level`, `points_total`, `cash_balance`, `is_admin`, `lang`, `status`, `email_verified_at`, `created_at`, `updated_at`) VALUES
('관리자', 'admin', 'admin@somekorean.com', '$2y$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '참나무', 99999, 0.00, 1, 'ko', 'active', NOW(), NOW(), NOW());
