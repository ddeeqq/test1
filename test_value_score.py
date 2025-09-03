import pandas as pd
import mysql.connector

# MySQL 연결 설정
db_config = {
    'user': 'Park',
    'password': 'Park',
    'host': 'localhost',
    'database': 'used_car_db',
    'auth_plugin': 'mysql_native_password'
}

def calculate_value_score(df):
    """차량의 가성비 점수를 계산하는 함수"""
    df_copy = df.copy()
    
    print("데이터 샘플:")
    print(df_copy[['차종', '연식', '주행거리', '가격', '신차가격']].head())
    print("\n데이터 통계:")
    print(df_copy[['연식', '주행거리', '가격', '신차가격']].describe())
    
    # 필요한 컬럼이 있는지 확인
    required_columns = ['신차가격', '가격', '연식', '주행거리', '차종']
    if not all(col in df_copy.columns for col in required_columns):
        print("필요한 컬럼이 없습니다:", required_columns)
        return df_copy
    
    # 1. 신차 대비 중고차 가격 비율 점수 (가격이 낮을수록 좋음)
    df_copy['price_ratio'] = df_copy['가격'] / df_copy['신차가격']
    df_copy['price_score'] = 1 - df_copy['price_ratio'].clip(0, 1)
    
    print("\n가격 비율 분석:")
    print(f"가격 비율 범위: {df_copy['price_ratio'].min():.3f} ~ {df_copy['price_ratio'].max():.3f}")
    print(f"가격 점수 범위: {df_copy['price_score'].min():.3f} ~ {df_copy['price_score'].max():.3f}")
    
    # 2. 차량 연령 점수 (최신 연식일수록 좋음)
    min_year = df_copy['연식'].min()
    max_year = df_copy['연식'].max()
    year_range = max_year - min_year
    
    print(f"\n연식 범위: {min_year} ~ {max_year} (범위: {year_range})")
    
    if year_range > 0:
        df_copy['age_score'] = (df_copy['연식'] - min_year) / year_range
    else:
        df_copy['age_score'] = 1.0
        
    print(f"연식 점수 범위: {df_copy['age_score'].min():.3f} ~ {df_copy['age_score'].max():.3f}")
    
    # 3. 주행거리 점수 (적을수록 좋음)
    min_mileage = df_copy['주행거리'].min()
    max_mileage = df_copy['주행거리'].max()
    mileage_range = max_mileage - min_mileage
    
    print(f"\n주행거리 범위: {min_mileage:,} ~ {max_mileage:,} (범위: {mileage_range:,})")
    
    if mileage_range > 0:
        df_copy['mileage_score'] = 1 - ((df_copy['주행거리'] - min_mileage) / mileage_range)
    else:
        df_copy['mileage_score'] = 1.0
        
    print(f"주행거리 점수 범위: {df_copy['mileage_score'].min():.3f} ~ {df_copy['mileage_score'].max():.3f}")
    
    # 4. 차종별 인기도 점수
    car_popularity = df_copy['차종'].value_counts()
    max_popularity = car_popularity.max()
    min_popularity = car_popularity.min()
    popularity_range = max_popularity - min_popularity
    
    print(f"\n인기도 범위: {min_popularity} ~ {max_popularity} (범위: {popularity_range})")
    print("상위 5개 인기 차종:")
    print(car_popularity.head())
    
    if popularity_range > 0:
        df_copy['popularity_score'] = (df_copy['차종'].map(car_popularity) - min_popularity) / popularity_range
    else:
        df_copy['popularity_score'] = 1.0
        
    print(f"인기도 점수 범위: {df_copy['popularity_score'].min():.3f} ~ {df_copy['popularity_score'].max():.3f}")
    
    # 전체 가성비 점수 계산
    df_copy['value_score'] = (
        df_copy['price_score'] * 0.40 +        # 가격 점수 (40%)
        df_copy['age_score'] * 0.25 +          # 연식 점수 (25%)
        df_copy['mileage_score'] * 0.25 +      # 주행거리 점수 (25%)
        df_copy['popularity_score'] * 0.10     # 인기도 점수 (10%)
    ) * 100  # 100점 만점으로 변환
    
    print(f"\n최종 가성비 점수 범위: {df_copy['value_score'].min():.1f} ~ {df_copy['value_score'].max():.1f}")
    
    # 상위 10개 차량 출력
    print("\n가성비 상위 10개 차량:")
    top10 = df_copy.nlargest(10, 'value_score')[['차종', '차량명', '연식', '주행거리', '가격', '신차가격', 'value_score']]
    print(top10.to_string())
    
    return df_copy

# 테스트 실행
if __name__ == "__main__":
    try:
        conn = mysql.connector.connect(**db_config)
        
        query = """
        SELECT c.car_brand AS 브랜드,
               i.car_name AS 차종,
               c.car_type AS 차량종류,
               i.full_name AS 차량명,
               i.model_year AS 연식,
               i.mileage AS 주행거리,
               i.price AS 가격,
               c.newcar_price AS 신차가격
        FROM carname c
        JOIN carinfo i ON c.car_name = i.car_name
        WHERE i.price IS NOT NULL 
        AND i.mileage IS NOT NULL
        LIMIT 1000
        """
        
        car_data = pd.read_sql(query, conn)
        conn.close()
        
        print(f"총 데이터 수: {len(car_data)}")
        result = calculate_value_score(car_data)
        
    except Exception as e:
        print(f"오류 발생: {e}")