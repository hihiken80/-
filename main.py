import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    # 전송 결과 로그 남기기
    res = requests.post(url, json=payload)
    print(f"텔레그램 응답: {res.status_code}")

# 삼성증권 이벤트 페이지 (안티-봇 헤더 강화)
url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

try:
    print("삼성증권 데이터 읽기 시작...")
    response = requests.get(url, headers=headers, timeout=20)
    # 한글 깨짐 방지
    response.encoding = 'utf-8' 
    soup = BeautifulSoup(response.text, 'html.parser')

    # 이벤트 목록 추출 (삼성증권 전용 태그)
    events = soup.select('.event_table tbody tr')
    
    if events:
        first_event = events[0].select_one('td.subject a')
        if first_event:
            title = first_event.get_text(strip=True)
            print(f"발견한 이벤트 제목: {title}")
            
            # 테스트를 위해 중복 체크 파일(last_event.txt) 무시하고 무조건 발송
            msg = f"<b>[삼성증권 신규 이벤트]</b>\n\n제목: {title}\n\n<a href='{url}'>이벤트 페이지 보기</a>"
            send_telegram_msg(msg)
    else:
        print("페이지 구조가 변경되었거나 접근이 차단되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")

