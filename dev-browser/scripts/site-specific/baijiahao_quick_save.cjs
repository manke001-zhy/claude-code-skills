/**
 * 快速保存百家号登录状态
 * 在已登录的浏览器中保存cookies
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');

async function quickSave() {
  console.log('========================================');
  console.log('  快速保存百家号登录状态');
  console.log('========================================\n');

  console.log('[步骤 1] 启动浏览器...');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 50
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  console.log('[步骤 2] 访问百家号...');
  await page.goto('https://baijiahao.baidu.com/', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });

  console.log('\n请在浏览器中登录账号（如果还未登录）');
  console.log('登录成功后，等待10秒自动保存cookies...\n');

  // 等待10秒让用户完成登录
  await page.waitForTimeout(10000);

  // 检查当前URL
  const currentUrl = page.url();
  console.log(`当前页面: ${currentUrl}`);

  // 保存cookies
  console.log('\n[步骤 3] 保存登录状态...');
  const cookies = await context.cookies();

  // 确保目录存在
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }

  fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');

  console.log(`✅ Cookies已保存!`);
  console.log(`   位置: ${COOKIES_FILE}`);
  console.log(`   数量: ${cookies.length} 个cookies`);

  // 显示一些关键cookies
  const keyCookies = cookies.filter(c =>
    c.name.includes('token') ||
    c.name.includes('session') ||
    c.name.includes('id') ||
    c.name.includes('user')
  );

  if (keyCookies.length > 0) {
    console.log('\n关键cookies:');
    keyCookies.forEach(c => {
      console.log(`  - ${c.name}: ${c.value.substring(0, 20)}...`);
    });
  }

  console.log('\n========================================');
  console.log('  保存完成！5秒后自动关闭浏览器');
  console.log('========================================\n');

  await page.waitForTimeout(5000);
  await browser.close();

  console.log('✅ 浏览器已关闭');
  console.log('✅ 下次将自动使用此登录状态\n');
}

quickSave().catch(error => {
  console.error('❌ 发生错误:', error.message);
  process.exit(1);
});
