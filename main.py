import requests
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print("환경변수 오류: TOKEN 또는 ID가 없습니다.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    res = requests.post(url, json=payload)
    print(f"텔레그램 응답: {res.status_code}")

# 삼성증권 이벤트 게시판 직접 요청 주소
url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.samsungpop.com/',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

try:
    print("--- 삼성증권 접속 시도 시작 ---")
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    # 텍스트가 정상적으로 왔는지 확인
    if "이벤트" in response.text:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 이벤트 목록 추출
        events = soup.select('.event_table tbody tr')
        if events:
            first_event = events[0].select_one('td.subject a')
            if first_event:
                title = first_event.get_text(strip=True)
                print(f"성공! 최신 이벤트: {title}")
                
                # 중복 방지 무시하고 무조건 발송 (테스트용)
                msg = f"<b>[삼성증권 알림 성공]</b>\n\n{title}"
                send_telegram_msg(msg)
            else:
                print("제목 태그를 찾을 수 없습니다.")
        else:
            print("이벤트 목록(tr)이 비어 있습니다.")
    else:
        print("보안 차단됨: 실제 웹페이지 내용을 읽지 못했습니다.")
        print(f"응답 요약(앞부분): {response.text[:100]}")

except Exception as e:
    print(f"실행 중 오류 발생: {e}")
