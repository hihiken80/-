import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print("Error: 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    requests.get(url)

# 삼성증권 이벤트 페이지
url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"
headers = {'User-Agent': 'Mozilla/5.0'} # 차단 방지를 위한 헤더
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 삼성증권 이벤트 리스트 추출 (실제 테이블 구조 반영)
events = soup.select('.event_table tbody tr')

# 이전에 보낸 이벤트 제목 저장용 파일 확인
db_file = "last_event.txt"
if os.path.exists(db_file):
    with open(db_file, "r", encoding="utf-8") as f:
        last_event_title = f.read().strip()
else:
    last_event_title = ""

if events:
    # 가장 최신 이벤트 1개만 확인
    latest_event = events[0].select_one('td.subject a')
    if latest_event:
        title = latest_event.text.strip()
        
        # 새로운 이벤트가 있을 때만 텔레그램 발송
        if title != last_event_title:
            send_telegram_msg(f"🔔 삼성증권 신규 이벤트: {title}")
            # 최신 제목 업데이트
            with open(db_file, "w", encoding="utf-8") as f:
                f.write(title)
