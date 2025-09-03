import csv
import pandas as pd
import mysql.connector

CSV_FILE = "merged_clean.csv"  # 차종, 차량명, 연식, 주행거리, 가격
CSV_FILE2 = "car_name.csv"  # 브랜드, 차종, 차량종류, 신차가격
CSV_FILE3 = "usedcar_data.csv" # 연도, 총거래대수
CSV_FILE4 = "AllCarData.csv" # 연도, 총거래량
CSV_FILE5 = "kia_faq.csv"  # category, question, answer, site(선택)
CSV_FILE6 = "hyundai_faq.csv"  # category, question, answer, site(선택)

# MySQL 연결 설정
db_config = {
    'user': 'Park',    # MySQL 사용자 이름
    'password': 'Park',    # MySQL 비밀번호
    'host': 'localhost',        # MySQL 호스트 (로컬호스트
    'database': 'used_car_db',      # 사용할 데이터베이스 이름
    'auth_plugin': 'mysql_native_password'  # 인증 플러그인 설정
}


### 실행 안되면 encoding 방식 'cp949'로 바꿔보기 ###
def insert_data_to_db():
    # MySQL 데이터베이스 연결
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # car_name.csv 파일 읽기 및 데이터 삽입
    with open(CSV_FILE2, mode='r', encoding='cp949') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO CarName (car_brand, car_name, car_type, newcar_price) VALUES (%s, %s, %s, %s)",
                (row['브랜드'], row['차종'], row['차량종류'], int(row['신차가격']))
            )
    print("car_name.csv data inserted successfully.")



    # kcar_cars.csv 파일 읽기 및 데이터 삽입
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO CarInfo (car_name, full_name, model_year, mileage, price) VALUES (%s, %s, %s, %s, %s)",
                (row['차종'], row['차량명'], row['연식'], row['주행거리'], row['가격'])
            )
    print("kcar_cars.csv data inserted successfully.")

    # usedcar_data.csv 파일 읽기 및 데이터 삽입
    with open(CSV_FILE3, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO UsedCarData (yearNum, total_transactions) VALUES (%s, %s)",
                (row['연도'], row['총거래대수'])
            )
    print("usedcar_data.csv data inserted successfully.")

    # AllCarData.csv 파일 읽기 및 데이터 삽입
    with open(CSV_FILE4, mode='r', encoding='cp949') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO AllCarData (yearNum, total_transactions) VALUES (%s, %s)",
                (row['연도'], row['총거래대수'])
            )
    print("AllCarData.csv data inserted successfully.")

    conn.commit()
    cursor.close()
    conn.close()


def load_data_to_db(query):
    # MySQL 데이터베이스 연결
    conn = mysql.connector.connect(**db_config)

    df = pd.read_sql(query, conn)

    conn.close()
    return df

def insert_faq_data_to_db():
    # MySQL 데이터베이스 연결
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    with open(CSV_FILE5, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO car_faq (category, question, answer, site) VALUES (%s, %s, %s, %s)",
                (row['category'], row['question'], row['answer'], row.get('site'))  # site 컬럼은 없을 수 있으니 get 사용
            )
    with open(CSV_FILE6, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT IGNORE INTO car_faq (category, question, answer, site) VALUES (%s, %s, %s, %s)",
                (row['category'], row['question'], row['answer'], row.get('site'))  # site 컬럼은 없을 수 있으니 get 사용
            )
    print("FAQ data inserted successfully.")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    insert_data_to_db()
    insert_faq_data_to_db()