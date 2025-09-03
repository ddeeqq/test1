import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CSV_FILE = "kcar_cars.csv"
MAX_PAGES = 500  # 크롤링할 페이지 수
BASE_URL = "https://www.kcar.com/bc/search"

def init_driver(headless=True):
    """Selenium Chrome 드라이버 초기화"""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0 Safari/537.36"
    )
    
    driver = webdriver.Chrome(options=options)
    return driver

def get_car_info(driver):
    """현재 페이지에서 차량명, 연식, 주행거리, 가격을 추출"""
    car_data = []
    car_boxes = driver.find_elements(By.CSS_SELECTOR, "div.carListBox")
    
    for box in car_boxes:
        try:
            name = box.find_element(By.CSS_SELECTOR, "div.carName p.carTit a").text.strip()
            detail_elem = box.find_element(By.CSS_SELECTOR, "p.detailCarCon")
            spans = detail_elem.find_elements(By.TAG_NAME, "span")
            
            year = spans[0].text.strip() if len(spans) > 0 else ""
            mileage = spans[1].text.strip() if len(spans) > 1 else ""
            price = box.find_element(By.CSS_SELECTOR, "div.carExpIn p.carExp").text.strip()
            
            car_data.append([name, year, mileage, price])
        except Exception:
            continue
    return car_data

def get_car_models(driver):
    """_001~_007 접두사별로 차량 모델명을 7개의 리스트로 반환"""
    models_001, models_002, models_003, models_004, models_005, models_006, models_007 = [], [], [], [], [], [], []
    labels = driver.find_elements(By.CSS_SELECTOR, "label.el-checkbox")
    
    for label in labels:
        try:
            label_id = label.get_attribute("id")
            if label_id:
                label_id = label_id.strip()  # 공백 제거
                model_name = label.find_element(By.CLASS_NAME, "el-checkbox__label").text.strip()
                if model_name:
                    if label_id.startswith("_001"):
                        models_001.append(model_name)
                    elif label_id.startswith("_002"):
                        models_002.append(model_name)
                    elif label_id.startswith("_003"):
                        models_003.append(model_name)
                    elif label_id.startswith("_004"):
                        models_004.append(model_name)
                    elif label_id.startswith("_005"):
                        models_005.append(model_name)
                    elif label_id.startswith("_006"):
                        models_006.append(model_name)
                    elif label_id.startswith("_007"):
                        models_007.append(model_name)
        except Exception:
            continue

    models = [models_001, models_002, models_003, models_004, models_005, models_006, models_007]
    
    return models

def get_checked_car_models(driver):
    """_001~_007 접두사 차량 중 체크된 모델명을 리스트로 반환"""
    all_models = []
    labels = driver.find_elements(By.CSS_SELECTOR, "label.el-checkbox")
    
    for label in labels:
        try:
            label_id = label.get_attribute("id").strip()
            # _001~_007 접두사 체크
            if label_id.startswith(("_001", "_002", "_003", "_004", "_005", "_006", "_007")):
                # 체크 상태 확인
                input_span = label.find_element(By.CSS_SELECTOR, "span.el-checkbox__input")
                if "is-checked" in input_span.get_attribute("class"):
                    model_name = label.find_element(By.CLASS_NAME, "el-checkbox__label").text.strip()
                    if model_name:
                        all_models.append(model_name)
        except Exception:
            continue
    
    return all_models

def crawl_car_info(base_url, max_pages=5, csv_file=CSV_FILE):
    """차량 정보(차량명, 연식, 주행거리, 가격)를 버튼 클릭으로 페이지를 넘기며 크롤링 후 CSV 저장"""
    driver = init_driver()
    driver.get(base_url)
    time.sleep(random.uniform(3, 6))

    with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["차량명", "연식", "주행거리", "가격"])

    for page in range(1, max_pages + 1):
        print(f"\n=== 📄 Page {page} ===")
        cars = get_car_info(driver)
        for car in cars:
            with open(csv_file, mode="a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(car)

        try:
            wait = WebDriverWait(driver, 10)

            # iframe 전환 부분 제거
            # → 버튼은 iframe 안이 아니라 메인 DOM에 있는 경우가 많음

            # "다음" 버튼 찾기 (텍스트 or alt 속성 기반)
            next_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., '다음') or .//img[contains(@alt, '다음')]]")
            ))

            # disabled 여부 확인
            if "is-disabled" in next_btn.get_attribute("class"):
                print("마지막 페이지입니다. 크롤링을 종료합니다.")
                break

            # JavaScript로 클릭 (더 안정적)
            driver.execute_script("arguments[0].click();", next_btn)
            print("다음 페이지 버튼 클릭 성공.")

            time.sleep(random.uniform(3, 5))

        except Exception as e:
            print(f"다음 페이지 버튼을 찾을 수 없습니다: {e}")

            # 디버깅용: 버튼 후보 출력
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print("버튼 목록:")
            for b in buttons:
                print(b.get_attribute("outerHTML")[:200])  # 앞부분만 출력

            break

    driver.quit()
    print(f"\n✅ 차량 정보 크롤링 완료! 데이터가 '{csv_file}'에 저장되었습니다.")


def crawl_car_models(base_url):
    """모델명을 페이지별로 수집하여 리스트로 반환"""
    driver = init_driver()
    
    driver.get(base_url)
    time.sleep(random.uniform(3, 6))
    
    models = get_car_models(driver)
    
    driver.quit()
    print(f"\n✅ 모델명 크롤링 완료! 총 {len(models)}개 모델 수집")
    return sorted(models)

if __name__ == "__main__":
    # 1️⃣ 차량 정보 크롤링 실행
    crawl_car_info(BASE_URL, MAX_PAGES)

