/**
 * 保存百家号登录状态（cookies）
 * 在登录成功后运行此脚本
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');

async function saveCookies() {
  console.log('========================================');
  console.log('  保存百家号登录状态');
  console.log('========================================\n');

  console.log('[步骤 1] 启动浏览器...');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  console.log('[步骤 2] 打开百家号...');
  await page.goto('https://baijiahao.baidu.com/', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  await page.waitForTimeout(3000);

  // 检查登录状态
  const isLoggedIn = await page.evaluate(() => {
    return document.querySelector('[class*="avatar"]') !== null ||
           document.querySelector('[class*="user"]') !== null ||
           document.querySelector('.user-info') !== null ||
           !window.location.href.includes('login');
  });

  if (isLoggedIn) {
    console.log('[步骤 3] 检测到已登录状态');

    // 保存cookies
    const cookies = await context.cookies();

    // 确保目录存在
    if (!fs.existsSync(CACHE_DIR)) {
      fs.mkdirSync(CACHE_DIR, { recursive: true });
    }

    fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');

    console.log('✅ 登录状态已保存！');
    console.log(`   位置: ${COOKIES_FILE}`);
    console.log('\n下次运行百家号脚本时将自动使用此登录状态。');

  } else {
    console.log('⚠️  未检测到登录状态');
    console.log('请先在浏览器中完成登录，然后重新运行此脚本。');

    console.log('\n浏览器将保持打开30秒，请尽快登录...');
    await page.waitForTimeout(30000);

    // 再次检查并保存
    const cookies = await context.cookies();
    if (!fs.existsSync(CACHE_DIR)) {
      fs.mkdirSync(CACHE_DIR, { recursive: true });
    }
    fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');
    console.log('✅ Cookies已保存（可能包含登录状态）');
  }

  console.log('\n========================================');
  console.log('  完成！');
  console.log('========================================\n');

  await browser.close();
}

saveCookies().catch(error => {
  console.error('❌ 发生错误:', error.message);
  process.exit(1);
});
