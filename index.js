const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const axios = require('axios');

// 봇 탐지 우회(스텔스) 플러그인 적용
puppeteer.use(StealthPlugin());

const TOKEN = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

async function sendTelegram(text) {
  if (!TOKEN || !CHAT_ID) return;
  try {
    const url = `https://api.telegram.org/bot${TOKEN}/sendMessage`;
    await axios.post(url, {
      chat_id: CHAT_ID,
      text: text,
      parse_mode: 'HTML'
    });
    console.log("텔레그램 전송 완료");
  } catch (e) {
    console.log("텔레그램 전송 실패:", e.message);
  }
}

(async () => {
  console.log("--- 삼성증권(Node.js Stealth) 접속 시작 ---");
  
  const browser = await puppeteer.launch({
    headless: "new",
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--window-size=1920,1080'
    ]
  });

  const page = await browser.newPage();

  // 실제 사람처럼 보이게 설정
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  
  try {
    // 페이지 접속 (타임아웃 60초로 넉넉하게)
    await page.goto('https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // 테이블이 뜰 때까지 대기
    console.log("페이지 로딩 대기 중...");
    await page.waitForSelector('table.event_table tbody tr', { timeout: 30000 });

    // 데이터 추출
    const event = await page.evaluate(() => {
      const rows = document.querySelectorAll('table.event_table tbody tr');
      if (rows.length > 0) {
        const titleEl = rows[0].querySelector('td.subject a');
        return titleEl ? titleEl.innerText.trim() : null;
      }
      return null;
    });

    if (event) {
      console.log(`이벤트 발견: ${event}`);
      await sendTelegram(`<b>[삼성증권 이벤트(Node.js)]</b>\n\n${event}\n\n<a href="https://www.samsungpop.com/mbw/customer/noticeEvent.do?cmd=eventList">이동하기</a>`);
    } else {
      console.log("이벤트 목록을 찾지 못했습니다.");
    }

  } catch (error) {
    console.error("오류 발생:", error.message);
    // 에러 시 화면 스크린샷 찍는 기능은 생략 (로그로만 확인)
  } finally {
    await browser.close();
    console.log("--- 종료 ---");
  }
})();
