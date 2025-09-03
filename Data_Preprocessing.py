import pandas as pd
import numpy as np
import os # 파일 존재 여부 확인을 위해 import

def process_all_data():
    """
    폴더에 있는 모든 차량 데이터 소스를 자동으로 찾아 병합하고 정제하여 
    최종 'merged_clean.csv' 파일을 생성하는 전체 프로세스입니다.
    """
    
    # --- 1. 존재하는 모든 CSV 데이터 소스 찾아서 병합 ---
    # 처리할 모든 데이터 파일 목록
    all_files = ["kcar_cars.csv", "usedcar_data.csv", "AllCarData.csv"]
    
    # 현재 폴더에 실제로 존재하는 파일만 골라냅니다.
    existing_files = [f for f in all_files if os.path.exists(f)]
    
    # 처리할 파일이 하나도 없으면 오류 메시지를 보여주고 종료합니다.
    if not existing_files:
        print("[ERROR] 처리할 데이터 파일이 없습니다. kcar_cars.csv, usedcar_data.csv 등을 확인해주세요.")
        print("[INFO] KCar 데이터가 없다면 먼저 Crawling_data_KCar.py를 실행하여 kcar_cars.csv 파일을 생성해야 합니다.")
        return

    print(f"[INFO] 다음 파일들을 병합합니다: {existing_files}")
    

    df_list = [pd.read_csv(file, encoding='utf-8', encoding_errors='ignore') for file in existing_files]
    merged_df = pd.concat(df_list, ignore_index=True)
    

    car_name_df = pd.read_csv("car_name.csv", encoding="cp949")
    merged_df["차종"] = None

    for _, row in car_name_df.iterrows():
        nor_name = row["차종"]
        mask = merged_df["차량명"].str.contains(nor_name, na=False)
        merged_df.loc[mask, "차종"] = nor_name
    

    merged_df["연식"] = merged_df["연식"].astype(str).str.extract(r"(\d{2,4})").astype(float)

    merged_df["주행거리"] = (
        merged_df["주행거리"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("km", "", regex=False)
        .astype(float)
    )

    def clean_price(price_str):
        if pd.isna(price_str):
            return np.nan
        price_str = str(price_str).strip().replace(",", "").replace("만원", "")
        try:
            return int(price_str)
        except (ValueError, TypeError):
            return np.nan

    merged_df["가격"] = merged_df["가격"].apply(clean_price)
    

    final_df = merged_df.dropna(subset=["차량명", "연식", "주행거리", "가격", "차종"])
    final_df = final_df.drop_duplicates(subset=["차량명", "연식", "주행거리", "가격", "차종"])
    

    final_df = final_df.reset_index(drop=True)
    

    output_file = "merged_clean.csv"
    final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"[INFO] 모든 데이터 처리 완료! → {output_file}")
    print(f"최종 데이터 개수: {len(final_df)}개")


if __name__ == "__main__":
    # 데이터 처리 전체 프로세스 실행
    process_all_data()

