import streamlit as st
import pandas as pd
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import Data_input as Dinput

plt.rc("font", family="AppleGothic")

# --------------------------------------------------------------------------
# --- 1. 데이터베이스 연결 및 데이터 로딩 함수 ---
# --------------------------------------------------------------------------

# MySQL 연결 설정
db_config = {
    'user': 'Park',
    'password': 'Park',
    'host': 'localhost',
    'database': 'used_car_db',
    'auth_plugin': 'mysql_native_password'
}

@st.cache_data
def load_car_data():
    """데이터베이스에서 차량 데이터를 로드하는 함수"""
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
        """
        
        car_data = pd.read_sql(query, conn)
        conn.close()
        
        return car_data
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

@st.cache_data  
def load_analysis_data():
    """분석용 데이터를 데이터베이스에서 로딩"""
    try:
        conn = mysql.connector.connect(**db_config)
        
        usedcar_query = "SELECT * FROM usedcardata"
        allcar_query = "SELECT * FROM allcardata"
        
        usedcar_data = pd.read_sql(usedcar_query, conn)
        allcar_data = pd.read_sql(allcar_query, conn)
        
        conn.close()
        
        return usedcar_data, allcar_data
    except Exception as e:
        st.error(f"분석 데이터 로딩 중 오류가 발생했습니다: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data
def load_faq_data():
    """데이터베이스에서 FAQ 데이터를 로드하는 함수"""
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT category, question, answer FROM car_faq"
        faq_data = pd.read_sql(query, conn)
        conn.close()
        return faq_data
    except Exception as e:
        st.error(f"FAQ 데이터 로딩 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# --------------------------------------------------------------------------
# --- 2. 가성비 점수 계산 함수 ---
# --------------------------------------------------------------------------

def calculate_value_score(df, full_data):
    """차량의 가성비 점수를 계산하는 함수"""
    df_copy = df.copy()
    
    # 필요한 컬럼이 있는지 확인
    required_columns = ['신차가격', '가격', '연식', '주행거리', '차종']
    if not all(col in df_copy.columns for col in required_columns):
        return df_copy
    
    # 1. 신차 대비 중고차 가격 비율 점수 (가격이 낮을수록 좋음)
    df_copy['price_ratio'] = df_copy['가격'] / df_copy['신차가격']
    df_copy['price_score'] = 1 - df_copy['price_ratio'].clip(0, 1)
    
    # 2. 차량 연령 점수 (최신 연식일수록 좋음) - 전체 데이터 기준
    min_year = full_data['연식'].min()
    max_year = full_data['연식'].max()
    year_range = max_year - min_year
    if year_range > 0:
        df_copy['age_score'] = (df_copy['연식'] - min_year) / year_range
    else:
        df_copy['age_score'] = 1.0
    
    # 3. 주행거리 점수 (적을수록 좋음) - 전체 데이터 기준
    min_mileage = full_data['주행거리'].min()
    max_mileage = full_data['주행거리'].max()
    mileage_range = max_mileage - min_mileage
    if mileage_range > 0:
        df_copy['mileage_score'] = 1 - ((df_copy['주행거리'] - min_mileage) / mileage_range)
    else:
        df_copy['mileage_score'] = 1.0
    
    # 4. 차종별 인기도 점수 (같은 차종 등록 대수가 많을수록 좋음) - 전체 데이터 기준
    car_popularity = full_data['차종'].value_counts()
    min_popularity = car_popularity.min()
    max_popularity = car_popularity.max()
    popularity_range = max_popularity - min_popularity
    if popularity_range > 0:
        df_copy['popularity_score'] = (df_copy['차종'].map(car_popularity) - min_popularity) / popularity_range
    else:
        df_copy['popularity_score'] = 1.0
    
    # 전체 가성비 점수 계산 (가중평균)
    df_copy['value_score'] = (
        df_copy['price_score'] * 0.40 +        # 가격 점수 (40%)
        df_copy['age_score'] * 0.25 +          # 연식 점수 (25%)
        df_copy['mileage_score'] * 0.25 +      # 주행거리 점수 (25%)
        df_copy['popularity_score'] * 0.10     # 인기도 점수 (10%)
    ) * 100  # 100점 만점으로 변환
    
    return df_copy

# --------------------------------------------------------------------------
# --- 3. 데이터 필터링 함수 ---
# --------------------------------------------------------------------------
def filter_car_data(data, brand=None, car_type=None, min_year=None, max_year=None, 
                   min_price=None, max_price=None, min_mileage=None, max_mileage=None):
    """조건에 따라 차량 데이터를 필터링하는 함수"""
    filtered_data = data.copy()
    
    if brand and brand != "전체":
        filtered_data = filtered_data[filtered_data['브랜드'] == brand]
    
    if car_type and car_type != "전체":
        filtered_data = filtered_data[filtered_data['차량종류'] == car_type]
    
    if min_year:
        filtered_data = filtered_data[filtered_data['연식'] >= min_year]
    
    if max_year:
        filtered_data = filtered_data[filtered_data['연식'] <= max_year]
    
    if min_price:
        filtered_data = filtered_data[filtered_data['가격'] >= min_price]
    
    if max_price:
        filtered_data = filtered_data[filtered_data['가격'] <= max_price]
    
    if min_mileage:
        filtered_data = filtered_data[filtered_data['주행거리'] >= min_mileage]
    
    if max_mileage:
        filtered_data = filtered_data[filtered_data['주행거리'] <= max_mileage]
    
    return filtered_data

def get_analysis_data(data, analysis_type, group_by):
    """분석 데이터를 생성하는 함수"""
    if analysis_type == "평균 가격":
        return data.groupby(group_by)['가격'].mean().reset_index()
    elif analysis_type == "판매 대수":
        return data.groupby(group_by).size().reset_index(name='판매대수')
    elif analysis_type == "평균 주행거리":
        return data.groupby(group_by)['주행거리'].mean().reset_index()
    elif analysis_type == "신차-중고차 가격차이":
        result = data.groupby(group_by).agg({
            '신차가격': 'mean',
            '가격': 'mean'
        }).reset_index()
        result['가격차이'] = result['신차가격'] - result['가격']
        return result

# --------------------------------------------------------------------------
# --- 3. Streamlit 페이지 구성 ---
# --------------------------------------------------------------------------

def home_page():
    """홈페이지 UI 구성"""
    st.title("🚗 중고차 구매 고객을 위한 정보 제공 서비스")
    st.markdown("---")
    
    # 데이터 개요
    car_data = load_car_data()
    if not car_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 차량 수", len(car_data))
        
        with col2:
            st.metric("브랜드 수", car_data['브랜드'].nunique())
        
        with col3:
            st.metric("평균 가격", f"{car_data['가격'].mean():.0f}만원")
        
        with col4:
            st.metric("평균 주행거리", f"{car_data['주행거리'].mean():,.0f}km")
    
    # 자동차 거래 현황 분석
    try:
        query_1 = """
        SELECT 
            u.yearNum,
            u.total_transactions AS used_transactions,
            a.total_transactions AS all_transactions,
            ROUND(u.total_transactions / a.total_transactions * 100, 2) AS used_ratio_percent
        FROM usedcardata u
        JOIN allcardata a 
            ON u.yearNum = a.yearNum
        ORDER BY u.yearNum;
        """
        
        conn = mysql.connector.connect(**db_config)
        df_1 = pd.read_sql(query_1, conn)
        conn.close()
        
        df_1["all_transactions_yoy"] = df_1["all_transactions"].pct_change() * 100
        df_1["all_transactions_yoy"] = df_1["all_transactions_yoy"].round(2)
        
        st.header("📊 자동차 등록 현황 대비 중고차 거래량 전년 대비 증감률 및 비율")
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # 선 그래프 (중고차 거래량)
        ax1.plot(df_1["yearNum"], df_1["used_transactions"], marker="o", label="중고차 거래 비율", color="blue")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("중고차 거래 비율 (%)", color="blue")
        ax1.legend(loc="upper left")
        
        # 막대 그래프 (all_transactions 전년 대비 증감률)
        ax2 = ax1.twinx()
        ax2.bar(df_1["yearNum"], df_1["all_transactions_yoy"], alpha=0.3, color="orange", label="신차 등록 증감율(%)")
        ax2.set_ylabel("신차 등록 증감율(%)", color="orange")
        
        # 범례 합치기
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc="upper right")
        
        plt.title("신차 등록 증감률 및 중고차 거래 비율 (2015-2023)")
        plt.grid(True)
        
        st.pyplot(fig)
        
        st.markdown("신차 등록률이 감소하고 중고차 거래율이 증가하는 현상은, 소비자들이 새 차보다 중고차를 선호하게 되면서 중고차 시장이 점점 더 중요한 자동차 유통 채널로 자리 잡고 있음을 보여줍니다.")
        
        st.markdown("---")
        
        # 가성비 상위 10개 차량
        # 점수 계산을 위해 전체 데이터 사용
        all_cars_with_scores = calculate_value_score(car_data, car_data)
        
        df_unique = all_cars_with_scores.sort_values('value_score', ascending=False).drop_duplicates(subset='차종', keep='first')
        top10 = df_unique.head(10)
        
        st.title("가성비 상위 10개 차량")
        st.markdown("가성비 점수는 신차 가격 대비 중고차 가격, 연식, 주행 거리, 동일 모델 등록 대수(인기도)를 종합적으로 고려하여 계산되었습니다.")
        st.dataframe(top10[['차량명', '가격', 'value_score']].rename(columns={
            '차량명': '차량명',
            '가격': '중고차 가격(만원)',
            'value_score': '가성비 점수'
        }), use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")

def search_page():
    """차량 검색 페이지 UI 구성"""
    st.title("🔍 차량 검색 및 분석")
    st.markdown("---")
    
    # 데이터 로드
    car_data = load_car_data()
    if car_data.empty:
        st.error("데이터를 로드할 수 없습니다.")
        return
    
    # 세션 상태 초기화
    if 'filtered_results' not in st.session_state:
        st.session_state.filtered_results = pd.DataFrame()
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = pd.DataFrame()
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0
    
    # 사이드바 필터
    st.sidebar.header("검색 및 분석 옵션")
    
    # 브랜드 선택
    brands = ["전체"] + sorted(car_data['브랜드'].unique().tolist())
    selected_brand = st.sidebar.selectbox("브랜드", brands)
    
    # 차량종류 선택
    if selected_brand != "전체":
        available_types = car_data[car_data['브랜드'] == selected_brand]['차량종류'].unique()
    else:
        available_types = car_data['차량종류'].unique()
    
    car_types = ["전체"] + sorted(available_types.tolist())
    selected_type = st.sidebar.selectbox("차량종류", car_types)
    
    # 연식 범위
    min_year = int(car_data['연식'].min())
    max_year = int(car_data['연식'].max())
    year_range = st.sidebar.slider("연식 범위", min_year, max_year, (min_year, max_year))
    
    # 가격 범위
    min_price = int(car_data['가격'].min())
    max_price = int(car_data['가격'].max())
    price_range = st.sidebar.slider("가격 범위 (만원)", min_price, max_price, (min_price, max_price))
    
    # 주행거리 범위
    min_mileage = int(car_data['주행거리'].min())
    max_mileage = int(car_data['주행거리'].max())
    mileage_range = st.sidebar.slider("주행거리 범위 (km)", min_mileage, max_mileage, (min_mileage, max_mileage))
    
    st.sidebar.markdown("---")
    st.sidebar.header("분석 옵션")
    
    # 분석 유형 선택
    analysis_type = st.sidebar.selectbox("분석 유형", 
                                       ['브랜드별 분석', '연식별 분석', '차량종류별 분석'])
    
    # 분석 지표 선택
    if analysis_type == '브랜드별 분석':
        group_by = '브랜드'
        metric_options = ['평균 가격', '판매 대수', '평균 주행거리', '신차-중고차 가격차이']
    elif analysis_type == '연식별 분석':
        group_by = '연식'
        metric_options = ['평균 가격', '판매 대수', '평균 주행거리']
    else:  # 차량종류별 분석
        group_by = '차량종류'
        metric_options = ['평균 가격', '판매 대수', '평균 주행거리', '신차-중고차 가격차이']
    
    selected_metric = st.sidebar.selectbox('분석 지표', metric_options)
    
    # 검색 및 분석 실행 버튼
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("검색 실행", type="primary", use_container_width=True):
            filtered_data = filter_car_data(
                car_data,
                brand=selected_brand,
                car_type=selected_type,
                min_year=year_range[0],
                max_year=year_range[1],
                min_price=price_range[0],
                max_price=price_range[1],
                min_mileage=mileage_range[0],
                max_mileage=mileage_range[1]
            )
            # 가성비 점수 계산 (전체 데이터를 기준으로)
            if not filtered_data.empty:
                st.session_state.filtered_results = calculate_value_score(filtered_data, car_data)
            else:
                st.session_state.filtered_results = pd.DataFrame()
            st.session_state.page_number = 0
    
    with col2:
        if st.button("분석 실행", type="secondary", use_container_width=True):
            filtered_data = filter_car_data(
                car_data,
                brand=selected_brand,
                car_type=selected_type,
                min_year=year_range[0],
                max_year=year_range[1],
                min_price=price_range[0],
                max_price=price_range[1],
                min_mileage=mileage_range[0],
                max_mileage=mileage_range[1]
            )
            if not filtered_data.empty:
                st.session_state.analysis_results = get_analysis_data(filtered_data, selected_metric, group_by)
            else:
                st.session_state.analysis_results = pd.DataFrame()
    
    # 탭으로 결과 구분
    tab1, tab2 = st.tabs(["🔍 검색 결과", "📊 분석 결과"])
    
    with tab1:
        st.header("검색 결과")
        
        if st.session_state.filtered_results.empty:
            st.warning("필터 조건을 설정하고 '검색 실행' 버튼을 눌러주세요.")
        else:
            results = st.session_state.filtered_results
            
            # 가성비 상위 추천 차량
            if 'value_score' in results.columns:
                st.subheader("🏆 가성비 상위 추천 차량")
                top_recommendations = results.head(5)
                
                for idx, row in top_recommendations.iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2.5, 1.5])
                        with col1:
                            st.write(f"**{row['차량명']}**")
                            st.write(f"{row['브랜드']} | {row['차량종류']}")
                        with col2:
                            st.metric("가격", f"{row['가격']:,}만원")
                        with col3:
                            st.metric("연식", f"{row['연식']}년")
                            st.metric("주행거리", f"{row['주행거리']:,.0f}km")
                        with col4:
                            st.metric("가성비 점수", f"{row['value_score']:.1f}")
                        st.markdown("---")
            
            st.subheader("전체 검색 결과")
            
            # 페이지네이션
            items_per_page = 10
            start_idx = st.session_state.page_number * items_per_page
            end_idx = start_idx + items_per_page
            
            paginated_results = results.iloc[start_idx:end_idx]
            
            # 검색 결과 요약
            st.info(f"총 {len(results)}대의 차량이 검색되었습니다.")
            
            # 결과 테이블
            if not paginated_results.empty:
                display_columns = ['차량명', '브랜드', '차량종류', '연식', '주행거리', '가격', '신차가격']
                if 'value_score' in paginated_results.columns:
                    display_columns.append('value_score')
                    paginated_results = paginated_results.rename(columns={'value_score': '가성비 점수'})
                    display_columns[-1] = '가성비 점수'
                    
                # 주행거리 포맷팅
                formatted_results = paginated_results[display_columns].copy()
                if '주행거리' in formatted_results.columns:
                    formatted_results['주행거리'] = formatted_results['주행거리'].apply(lambda x: f"{x:,.0f}km")
                
                st.dataframe(
                    formatted_results,
                    use_container_width=True,
                    hide_index=True
                )
            
            # 페이지네이션 버튼
            total_items = len(results)
            total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
            
            st.markdown(f"페이지: **{st.session_state.page_number + 1} / {total_pages}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("이전 페이지", disabled=(st.session_state.page_number <= 0)):
                    st.session_state.page_number -= 1
                    st.rerun()
            with col2:
                if st.button("다음 페이지", disabled=(st.session_state.page_number >= total_pages - 1)):
                    st.session_state.page_number += 1
                    st.rerun()
    
    with tab2:
        st.header(f"{analysis_type} - {selected_metric}")
        
        if st.session_state.analysis_results.empty:
            st.warning("분석 조건을 설정하고 '분석 실행' 버튼을 눌러주세요.")
        else:
            analysis_result = st.session_state.analysis_results
            
            # 분석 결과 시각화
            if selected_metric == "평균 가격":
                st.bar_chart(analysis_result.set_index(group_by)['가격'])
                st.dataframe(analysis_result, use_container_width=True, hide_index=True)
            
            elif selected_metric == "판매 대수":
                st.bar_chart(analysis_result.set_index(group_by)['판매대수'])
                st.dataframe(analysis_result, use_container_width=True, hide_index=True)
            
            elif selected_metric == "평균 주행거리":
                st.bar_chart(analysis_result.set_index(group_by)['주행거리'])
                st.dataframe(analysis_result, use_container_width=True, hide_index=True)
            
            elif selected_metric == "신차-중고차 가격차이":
                st.bar_chart(analysis_result.set_index(group_by)['가격차이'])
                st.dataframe(analysis_result, use_container_width=True, hide_index=True)

def analysis_page():
    """빈 분석 페이지 - 추후 기능 추가 예정"""
    st.title("📊 추가 기능")
    st.markdown("---")
    
    st.info("🚧 이 페이지는 현재 개발 중입니다.")
    st.write("")
    st.write("향후 추가될 기능:")
    st.write("• 고급 데이터 분석 도구")
    st.write("• 시장 동향 분석")
    st.write("• 예측 모델링")
    st.write("• 맞춤형 리포트 생성")
    
    st.write("")
    st.write("")
    st.write("현재는 '차량 검색' 페이지에서 기본적인 분석 기능을 이용하실 수 있습니다.")

def faq_page():
    """FAQ 페이지 UI 구성"""
    st.title("💬 자주 묻는 질문 (FAQ)")
    st.markdown("---")

    faq_data = load_faq_data()

    if faq_data.empty:
        st.warning("FAQ 데이터가 없습니다.")
        return

    # 카테고리별로 그룹화
    categories = faq_data['category'].unique()

    for category in categories:
        st.subheader(f"📂 {category}")
        
        # 해당 카테고리의 질문과 답변
        category_faqs = faq_data[faq_data['category'] == category]
        
        for _, row in category_faqs.iterrows():
            with st.expander(f"Q. {row['question']}"):
                st.write(row['answer'])
        
        st.markdown("---")

# --- 메인 실행 로직 ---
def main():
    st.set_page_config(
        page_title="중고차 분석 시스템",
        page_icon="🚗",
        layout="wide"
    )
    
    st.sidebar.title("메뉴")
    page_options = ["홈", "차량 검색", "추가 기능", "FAQ"]
    selected_page = st.sidebar.radio("페이지를 선택하세요", page_options)
    
    if selected_page == "홈":
        home_page()
    elif selected_page == "차량 검색":
        search_page()
    elif selected_page == "추가 기능":
        analysis_page()
    elif selected_page == "FAQ":
        faq_page()

if __name__ == "__main__":
    main()
