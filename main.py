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

# 삼성증권 보안망을 통과하기 위한 실제 데이터 요청 주소
api_url = "https://www.samsungpop.com/mbw/customer/noticeEvent.do"
params = {
    "cmd": "eventList",
    "MENU_ID": "M1231757761593",
    "isSearch": "Y"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'X-Requested-With': 'XMLHttpRequest', # 실제 브라우저인 척 속이는 핵심 헤더
    'Referer': 'https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList'
}

try:
    print("--- 삼성증권 API 직접 호출 시작 ---")
    # 보안 통과를 위해 POST 방식과 세션 데이터 흉내
    response = requests.post(api_url, headers=headers, params=params, timeout=30)
    response.encoding = 'utf-8'
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 데이터가 포함된 테이블 본문 탐색
    rows = soup.select('table.event_table tbody tr')
    
    if rows:
        # 제목이 포함된 첫 번째 항목 추출
        first_row = rows[0].select_one('td.subject a')
        if first_row:
            title = first_row.get_text(strip=True)
            print(f"이벤트 획득 성공: {title}")
            
            # 텔레그램 발송 (테스트를 위해 중복 체크 잠시 해제)
            msg = f"<b>[삼성증권 이벤트 알림]</b>\n\n제목: {title}\n\n<a href='{api_url}?cmd=eventList'>이벤트 페이지 바로가기</a>"
            send_telegram_msg(msg)
        else:
            print("데이터 구조가 변경되었습니다.")
    else:
        # 차단되었을 경우 응답 내용 일부 출력하여 원인 파악
        print("API 응답 내에 데이터가 없습니다. (보안 차단 가능성)")
        print(f"응답 요약: {response.text[:150]}")

except Exception as e:
    print(f"시스템 오류 발생: {e}")
