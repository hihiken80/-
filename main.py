import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList"

BOT_TOKEN = "여기에_봇토큰"
CHAT_ID = "여기에_챗아이디"

SAVE_FILE = "last_events.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.samsungpop.com/"
}

session = requests.Session()
session.headers.update(HEADERS)

def fetch_events():
    r = session.get(URL, timeout=15)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    events = []
    for a in soup.select("a[href*='eventView']"):
        title = a.get_text(strip=True)
        link = "https://www.samsungpop.com" + a["href"]
        if title:
            events.append(f"{title}|{link}")

    return list(dict.fromkeys(events))  # 중복 제거


def load_old():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()


def save_new(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(data))


def send_telegram(msg):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(api, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })


def main():
    events = fetch_events()
    old = load_old()

    new_items = [e for e in events if e not in old]

    if new_items:
        for item in new_items:
            title, link = item.split("|")
            message = f"📢 삼성증권 새 이벤트\n\n{title}\n{link}"
            send_telegram(message)

        save_new(events)


if __name__ == "__main__":
    main()
