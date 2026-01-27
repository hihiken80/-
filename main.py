import requests
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    res = requests.post(url, json=payload)
    print(f"텔레그램 응답: {res.status_code}")

# 삼성증권 이벤트 목록 조회 API (보안이 낮은 경로)
url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do"
params = {
    "cmd": "eventList",
    "MENU_ID": "M1231757761593",
    "isSearch": "Y"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.samsungpop.com/',
    'X-Requested-With': 'XMLHttpRequest'
}

try:
    print("삼성증권 보안 우회 접속 중...")
    # POST 방식으로 요청하여 봇 감지 회피
    response = requests.post(url, headers=headers, params=params, timeout=30)
    response.encoding = 'utf-8'
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 실제 이벤트 데이터가 담긴 테이블 행 추출
    events = soup.select('table.event_table tbody tr')
    
    if events:
        # 첫 번째 행에서 제목과 날짜 추출
        latest = events[0]
        title_element = latest.select_one('td.subject a')
        
        if title_element:
            title = title_element.get_text(strip=True)
            print(f"최신 이벤트 확인: {title}")
            
            # 중복 알림 방지 로직
            db_file = "last_event.txt"
            if os.path.exists(db_file):
                with open(db_file, "r", encoding="utf-8") as f:
                    if f.read().strip() == title:
                        print("이미 알림을 보낸 이벤트입니다.")
                        exit()

            # 메시지 구성 및 발송
            msg = f"<b>[삼성증권 신규 이벤트]</b>\n\n{title}\n\n<a href='https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList'>이벤트 페이지 이동</a>"
            send_telegram_msg(msg)
            
            with open(db_file, "w", encoding="utf-8") as f:
                f.write(title)
        else:
            print("데이터 구조가 변경되었습니다. 수동 점검 필요.")
    else:
        print("접속은 성공했으나 데이터를 찾지 못했습니다. (보안 차단 가능성)")

except Exception as e:
    print(f"실행 오류: {e}")

