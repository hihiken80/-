import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def get_samsung_event():
    print("--- 브라우저 설정 초기화 ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 화면 없이 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 봇 탐지 회피를 위한 헤더 설정
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"
        print(f"접속 시도: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기 (최대 20초)
        print("페이지 로딩 대기 중...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.event_table"))
        )
        
        # 데이터 추출
        events = driver.find_elements(By.CSS_SELECTOR, "table.event_table tbody tr")
        
        if events:
            first_event = events[0].find_element(By.CSS_SELECTOR, "td.subject a")
            title = first_event.text.strip()
            print(f"★ 이벤트 발견 성공: {title}")
            
            # 텔레그램 발송 (테스트용 무조건 발송)
            msg = f"<b>[삼성증권 이벤트]</b>\n\n{title}\n\n<a href='{url}'>바로가기</a>"
            send_telegram_msg(msg)
        else:
            print("테이블은 찾았으나 이벤트 목록이 비어있습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        # 오류 시 현재 페이지 소스 일부 출력 (디버깅용)
        print(f"페이지 소스 요약: {driver.page_source[:200]}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_samsung_event()
