const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const axios = require('axios');

puppeteer.use(StealthPlugin());

const TOKEN = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

async function sendTelegram(text) {
  if (!TOKEN || !CHAT_ID) return;
  try {
    await axios.post(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
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
  console.log("--- KODEX 이벤트 페이지 접속 시작 ---");
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  try {
    const url = 'https://www.funetf.co.kr/membersLounge/event';
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

    // 이벤트 리스트가 로딩될 때까지 대기
    console.log("페이지 로딩 대기 중...");
    await page.waitForSelector('.event-list-wrap', { timeout: 30000 });

    // 데이터 추출
    const eventData = await page.evaluate(() => {
      // 진행 중인 이벤트 목록 중 첫 번째 항목 선택
      const firstEvent = document.querySelector('.event-list-wrap ul li .txt-area');
      if (firstEvent) {
        const title = firstEvent.querySelector('strong')?.innerText.trim();
        const date = firstEvent.querySelector('.date')?.innerText.trim();
        return { title, date };
      }
      return null;
    });

    if (eventData && eventData.title) {
      console.log(`이벤트 발견: ${eventData.title}`);
      
      // 중복 알림 방지를 위한 처리 생략(테스트를 위해 무조건 발송)
      const msg = `<b>[KODEX 새 이벤트]</b>\n\n제목: ${eventData.title}\n기간: ${eventData.date}\n\n<a href="${url}">이벤트 페이지 바로가기</a>`;
      await sendTelegram(msg);
    } else {
      console.log("진행 중인 이벤트를 찾지 못했습니다.");
    }

  } catch (error) {
    console.error("오류 발생:", error.message);
  } finally {
    await browser.close();
    console.log("--- 작업 종료 ---");
  }
})();
