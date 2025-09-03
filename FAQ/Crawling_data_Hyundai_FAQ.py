from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv

CSV_FILE = "hyundai_faq.csv"

# FAQEntry 클래스
class FAQEntry:
    def __init__(self, category, question, answer, site):
        self.category = category
        self.question = question
        self.answer = answer
        self.site = site

    def __repr__(self):
        return f'FAQEntry<category={self.category}, question={self.question}, answer={self.answer}, site={self.site}>'

# 1. Chrome 실행
path = 'chromedriver.exe'
service = webdriver.chrome.service.Service(path)
driver = webdriver.Chrome(service=service)

# 2. FAQ 페이지 접속
site_name = "현대자동차"
url = "https://certified.hyundai.com/p/cs/faq/faqUi.do?q=pc"
driver.get(url)

faq_list = []
time.sleep(3)  

# 더보기 버튼을 끝까지 클릭한 후 항목 가져오기 시작
while True:
    try:
        more_btn = driver.find_element(By.CSS_SELECTOR, ".btn_more")
        if more_btn.is_displayed():
            driver.execute_script("arguments[0].click();", more_btn)
            time.sleep(1) 
        else:
            break
    except:
        break 

# 3. FAQ 항목 찾기
faq_items = driver.find_elements(By.CSS_SELECTOR, "ul#csFaqList > li.cont")

for item in faq_items:
    try:
        category_elem = item.find_element(By.CSS_SELECTOR, "p > span.qa_name_txt")
        category = category_elem.text.strip()

        question_elem = item.find_element(By.CSS_SELECTOR, "button.js_toggle")
        question = question_elem.text.strip()

        toggle_btn = item.find_element(By.CSS_SELECTOR, "button.js_toggle")
        driver.execute_script("arguments[0].click();", toggle_btn)
        time.sleep(0.3)

        answer_elem = item.find_element(By.CSS_SELECTOR, "div.gray_box > p")
        answer = answer_elem.text.strip()

        faq_list.append(FAQEntry(category, question, answer, site_name))
    except Exception as e:
        print("에러 발생:", e)

# 4. CSV 저장
with open(CSV_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["Category", "Question", "Answer", "Site"])
    
    for faq in faq_list:
        writer.writerow([faq.category, faq.question, faq.answer, site_name])
        print(faq)

    driver.quit()

print(f"CSV 저장 완료: {CSV_FILE}")


'''
connection = mysql.connector.connect(
    host='localhost',
    user='ohgiraffers',
    password='ohgiraffers',
    database='faqdb'
)
cursor = connection.cursor()

for row in faq_list:
    sql = "INSERT INTO faq_table(category, question, answer, site) VALUES (%s, %s, %s, %s)"
    values = (row.category, row.question, row.answer, row.site)
    cursor.execute(sql, values)

connection.commit()
cursor.close()
connection.close()
'''

