import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    events = soup.select('.event_table tbody tr')
    
    if events:
        latest_event = events[0].select_one('td.subject a')
        if latest_event:
            title = latest_event.get_text(strip=True)
            # 테스트를 위해 중복 체크 없이 즉시 발송
            msg = f"<b>[삼성증권 이벤트 확인]</b>\n\n최신이벤트: {title}\n\n정상 작동 중입니다."
            send_telegram_msg(msg)
            print("메시지 발송 완료")
    else:
        print("목록을 찾지 못함")
except Exception as e:
    print(f"오류: {e}")
