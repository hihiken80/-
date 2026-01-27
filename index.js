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
  } catch (e) { console.log("전송 실패"); }
}

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  
  // 1. 모바일 기기(아이폰)처럼 보이도록 설정
  await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1');
  await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });

  try {
    // 2. 모바일 전용 이벤트 페이지 주소로 접속
    console.log("모바일 페이지 접속 시도...");
    await page.goto('https://m.samsungpop.com/customer/notice/event.do', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // 3. 페이지 로딩을 위해 5초간 대기
    await new Promise(r => setTimeout(r, 5000));

    // 4. 모바일 페이지 구조에 맞춰 데이터 추출 (구조가 다를 수 있음)
    const eventTitle = await page.evaluate(() => {
      // 모바일 페이지의 리스트 항목을 찾습니다.
      const firstItem = document.querySelector('.event_list li .title, .list_type01 li a');
      return firstItem ? firstItem.innerText.trim() : null;
    });

    if (eventTitle) {
      console.log(`성공: ${eventTitle}`);
      await sendTelegram(`<b>[삼성증권 모바일 우회 성공]</b>\n\n${eventTitle}`);
    } else {
      // 실패 시 현재 페이지의 텍스트 일부를 출력하여 상태 확인
      const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 100));
      console.log(`내용을 찾지 못함. 페이지 일부: ${bodyText}`);
    }

  } catch (error) {
    console.error("차단됨 또는 타임아웃:", error.message);
  } finally {
    await browser.close();
  }
})();
