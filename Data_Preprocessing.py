import pandas as pd
import numpy as np

def merge_car_data(car_file, name_file, output_file = "merged.csv"):

    """
    차량 정보와 기본 이름 데이터를 병합하여 merged.csv 생성
    """

    data1 = pd.read_csv(car_file)  # 차량명(풀네임), 연식, 주행거리, 가격
    data2 = pd.read_csv(name_file, encoding="cp949")  # 차량브랜드, 차량명(기본 이름)

    # Create a new column for basic car name
    data1["차종"] = None

    # data2의 기본 이름이 data1의 차량명에 포함되면 추가
    for _, row in data2.iterrows():
        nor_name = row["차종"] 
        mask = data1["차량명"].str.contains(nor_name, na=False)
        data1.loc[mask, "차종"] = nor_name

    # 중복 제거
    data1 = data1.drop_duplicates(subset=["차량명", "연식", "주행거리", "가격", "차종"])

    data1.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"[INFO] 병합 완료 → {output_file}")



def clean_merged_data(input_file="merged.csv", output_file="merged_clean.csv"):

    """
    merged.csv를 정제하여 merged_clean.csv 생성
    """

    data = pd.read_csv(input_file, encoding="cp949")

    # 연식: 앞 2자리 숫자 추출 후 정수 변환
    data["연식"] = data["연식"].astype(str).str.extract(r"(\d{2})").astype(float)

    # 주행거리: ','와 'km' 제거 후 숫자로 변환
    data["주행거리"] = (
        data["주행거리"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("km", "", regex=False)
        .astype(float)
    )

    # 가격 처리
    def clean_price(price_str):
        if pd.isna(price_str):
            return np.nan
        price_str = str(price_str).strip()
        # 첫 글자가 숫자가 아니면 NaN
        if not price_str[0].isdigit():
            return np.nan
        # 공백 기준으로 첫 번째 값만
        first_price = price_str.split()[0]
        # ','와 '만원' 제거
        first_price = first_price.replace(",", "").replace("만원", "")
        try:
            return int(first_price)
        except:
            return np.nan

    # 가격 정리
    data["가격"] = data["가격"].apply(clean_price)

    # NaN이 있는 행 제거
    data = data.dropna(subset=["가격", "차종"])

    # 결과 저장
    data.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"[INFO] 정제 완료 → {output_file}")

    return data

if __name__ == "__main__":
    # 1️⃣ 차량 정보 크롤링 실행
    merge_car_data("kcar_cars.csv", "car_name.csv", "merged.csv")
    # 2️⃣ 병합된 데이터 정제 실행
    clean_merged_data("merged.csv", "merged_clean.csv")
