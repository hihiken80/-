import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print("오류: 환경변수(TOKEN/ID)를 찾을 수 없습니다.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    res = requests.post(url, json=payload)
    print(f"텔레그램 응답 코드: {res.status_code}")
    print(f"텔레그램 응답 내용: {res.text}")

# 테스트용 네이버 블로그 RSS (글이 매우 자주 올라오는 공식 블로그)
rss_url = "https://rss.blog.naver.com/blogcorp.xml" 

try:
    print("데이터 가져오기 시도 중...")
    response = requests.get(rss_url, timeout=15)
    soup = BeautifulSoup(response.text, 'xml')
    items = soup.find_all('item')

    if items:
        title = items[0].find('title').get_text()
        link = items[0].find('link').get_text()
        print(f"최신 글 발견: {title}")
        
        # 테스트를 위해 중복 체크 없이 무조건 발송
        msg = f"<b>[블로그 알림 테스트]</b>\n\n제목: {title}\n\n<a href='{link}'>링크 바로가기</a>"
        send_telegram_msg(msg)
    else:
        print("RSS 항목을 찾을 수 없습니다.")
except Exception as e:
    print(f"코드 실행 중 에러 발생: {e}")
