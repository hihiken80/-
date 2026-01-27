import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    res = requests.post(url, json=payload)
    print(f"텔레그램 응답: {res.status_code}")

# 삼성증권 이벤트 주소
url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"

# 차단을 피하기 위한 헤더 세트
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://m.samsungpop.com/',
    'Connection': 'keep-alive'
}

try:
    print("데이터 읽기 시도 중...")
    # 접속 차단을 피하기 위해 세션 유지 방식 사용
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # 이벤트 테이블 안의 모든 행(tr)을 가져옵니다.
    events = soup.find_all('tr')
    
    found = False
    if events:
        for row in events:
            # 제목이 들어있는 'subject' 클래스 탐색
            subject_td = row.find('td', class_='subject')
            if subject_td:
                title_tag = subject_td.find('a')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    print(f"이벤트 발견: {title}")
                    
                    # 텔레그램 발송
                    msg = f"<b>[삼성증권 이벤트]</b>\n\n{title}\n\n<a href='{url}'>페이지 이동</a>"
                    send_telegram_msg(msg)
                    found = True
                    break # 가장 최신 하나만 보내고 종료

    if not found:
        print("이벤트를 찾지 못했습니다. 구조 분석이 더 필요합니다.")
        # 만약 차단되었다면 전체 텍스트 일부 출력해서 확인
        print(f"응답 요약: {response.text[:200]}")

except Exception as e:
    print(f"오류: {e}")
