-- MySQL 인증 플러그인 문제 해결을 위한 SQL 명령어들
-- MySQL 관리자 권한으로 실행해주세요

-- 1. 기존 사용자 삭제 (있다면)
DROP USER IF EXISTS 'Park'@'localhost';

-- 2. mysql_native_password로 새 사용자 생성
CREATE USER 'Park'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Park';

-- 3. 권한 부여
GRANT ALL PRIVILEGES ON used_car_db.* TO 'Park'@'localhost';

-- 4. 권한 적용
FLUSH PRIVILEGES;

-- 5. 사용자 확인
SELECT user, host, plugin FROM mysql.user WHERE user = 'Park';