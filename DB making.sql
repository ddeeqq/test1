-- 데이터 베이스 및 테이블 생성

CREATE DATABASE IF NOT EXISTS used_car_db;

USE used_car_db;

CREATE TABLE IF NOT EXISTS CarName (
    car_name VARCHAR(50) PRIMARY KEY,
    car_brand VARCHAR(50) NOT NULL,
    car_type ENUM('경차', '승용차', 'SUV', '승합차', '트럭'),
    newcar_price INT NOT NULL
);

CREATE TABLE IF NOT EXISTS CarInfo (
    car_ID INT AUTO_INCREMENT PRIMARY KEY,
    car_name VARCHAR(50),
    full_name VARCHAR(100) NOT NULL,
    mileage INT,
    model_year INT,
    price INT NOT NULL,
    FOREIGN KEY (car_name) REFERENCES CarName(car_name)
);

CREATE TABLE IF NOT EXISTS car_faq (
    faq_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    site VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS UsedCarData (
    yearNum INT PRIMARY KEY,
    total_transactions INT NOT NULL
);

CREATE TABLE IF NOT EXISTS AllCarData (
    yearNum INT PRIMARY KEY,
    total_transactions INT NOT NULL
);



-- 데이터 삽입

INSERT INTO CarName (car_name, car_brand, car_type, newcar_price) VALUES (%s, %s, %s, %s);
INSERT INTO CarInfo (car_name, full_name, mileage, model_year, price) VALUES (%s, %s, %s, %s, %s);
INSERT INTO UsedCarData (yearNum, total_transactions) VALUES (%s, %s);


-- 데이터 조회

-- 브랜드별 평균 중고차 가격
SELECT c.car_brand,  COUNT(*),
       AVG(i.price) AS avg_used_price
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_brand
ORDER BY avg_used_price DESC;

-- 차량 종류별 평균 중고차 가격
SELECT c.car_brand,  COUNT(*),
       AVG(i.price) AS avg_used_price
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_type
ORDER BY avg_used_price DESC;

-- 브랜드-차량 종류별 평균 중고차 가격
SELECT c.car_brand,  COUNT(*),
        AVG(i.price) AS avg_used_price
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_brand, c.car_type
ORDER BY avg_used_price DESC;

-- 연식별 평균 중고차 가격
SELECT i.model_year, COUNT(*),
       AVG(i.price) AS avg_used_price
FROM CarInfo i
GROUP BY i.model_year
ORDER BY i.model_year DESC;

-- 연식-브랜드별 평균 중고차 가격
SELECT i.model_year,
       c.car_brand,  COUNT(*),
       AVG(i.price) AS avg_used_price
FROM CarInfo i
JOIN CarName c ON i.car_name = c.car_name
GROUP BY i.model_year, c.car_brand
ORDER BY i.model_year DESC, avg_used_price DESC;

-- 브랜드별 평균 주행 거리
SELECT c.car_brand,  COUNT(*),
       AVG(i.mileage) AS avg_mileage
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_brand
ORDER BY avg_mileage DESC;

-- 브랜드별 신차가격 - 중고차 평균가격  차이
SELECT c.car_brand,
       AVG(c.newcar_price) AS avg_newcar_price,
       AVG(i.price) AS avg_used_price,
       (AVG(c.newcar_price) - AVG(i.price)) AS price_difference
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_brand
ORDER BY price_difference DESC;

-- 차량 종류별 신차가격 - 중고차 평균가격  차이
SELECT c.car_type,
        AVG(c.newcar_price) AS avg_newcar_price,
        AVG(i.price) AS avg_used_price,
        (AVG(c.newcar_price) - AVG(i.price)) AS price_difference
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_type
ORDER BY price_difference DESC;

-- 브랜드별 중고차 등록 대수
SELECT c.car_brand,
       COUNT(i.car_ID) AS total_used_cars
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_brand
ORDER BY total_used_cars DESC;

-- 차량 종류별 중고차 등록 대수
SELECT c.car_type,
       COUNT(i.car_ID) AS total_used_cars
FROM CarName c
JOIN CarInfo i ON c.car_name = i.car_name
GROUP BY c.car_type
ORDER BY total_used_cars DESC;

-- 가격 범위별 중고차 등록 대수
SELECT
    CASE
        WHEN i.price < 5000000 THEN '0-5백만원'
        WHEN i.price BETWEEN 5000000 AND 10000000 THEN '5백만원-1천만원'
        WHEN i.price BETWEEN 10000000 AND 20000000 THEN '1천만원-2천만원'
        WHEN i.price BETWEEN 20000000 AND 30000000 THEN '2천만원-3천만원'
        WHEN i.price BETWEEN 30000000 AND 40000000 THEN '3천만원-4천만원'
        WHEN i.price BETWEEN 40000000 AND 50000000 THEN '4천만원-5천만원'
        ELSE '5천만원 이상'
    END AS price_range,
    COUNT(i.car_ID) AS total_used_cars
FROM CarInfo i
GROUP BY price_range
ORDER BY total_used_cars DESC;