/**
 * 完整保存百家号登录状态
 * 保存cookies、localStorage、sessionStorage
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'baijiahao-storage.json');

async function fullSave() {
  console.log('========================================');
  console.log('  完整保存百家号登录状态');
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

  console.log('\n⏳ 请在浏览器中完成登录');
  console.log('⏳ 等待20秒，期间请完成登录操作...\n');

  // 等待20秒让用户完成登录
  for (let i = 20; i > 0; i--) {
    process.stdout.write(`\r倒计时: ${i}秒 `);
    await page.waitForTimeout(1000);
  }
  console.log('\n');

  // 检查登录状态
  const isLoggedIn = await page.evaluate(() => {
    const url = window.location.href;
    const hasAvatar = document.querySelector('[class*="avatar"]') !== null;
    const hasUser = document.querySelector('[class*="user"]') !== null;
    const notLoginPage = !url.includes('login');

    return {
      url,
      hasAvatar,
      hasUser,
      notLoginPage,
      likelyLoggedIn: notLoginPage && (hasAvatar || hasUser)
    };
  });

  console.log('登录状态检测:');
  console.log(`  URL: ${isLoggedIn.url}`);
  console.log(`  可能已登录: ${isLoggedIn.likelyLoggedIn ? '是' : '否'}\n`);

  // 保存cookies
  console.log('[步骤 3] 保存Cookies...');
  const cookies = await context.cookies();

  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }

  fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');
  console.log(`✅ Cookies已保存 (${cookies.length}个)`);

  // 保存localStorage
  console.log('[步骤 4] 保存LocalStorage...');
  const localStorage = await page.evaluate(() => {
    const storage = [];
    for (let i = 0; i < localStorage.length; i++) {
      const name = localStorage.key(i);
      const value = localStorage.getItem(name);
      storage.push({ name, value });
    }
    return storage;
  });

  // 保存sessionStorage
  console.log('[步骤 5] 保存SessionStorage...');
  const sessionStorage = await page.evaluate(() => {
    const storage = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const name = sessionStorage.key(i);
      const value = sessionStorage.getItem(name);
      storage.push({ name, value });
    }
    return storage;
  });

  const storageData = {
    origin: 'https://baijiahao.baidu.com',
    localStorage: localStorage,
    sessionStorage: sessionStorage,
    savedAt: new Date().toISOString()
  };

  fs.writeFileSync(STORAGE_FILE, JSON.stringify(storageData, null, 2), 'utf-8');
  console.log(`✅ LocalStorage已保存 (${localStorage.length}项)`);
  console.log(`✅ SessionStorage已保存 (${sessionStorage.length}项)`);

  // 显示关键信息
  if (localStorage.length > 0) {
    console.log('\n关键LocalStorage项:');
    localStorage
      .filter(item =>
        item.name.includes('token') ||
        item.name.includes('user') ||
        item.name.includes('id') ||
        item.name.includes('session')
      )
      .slice(0, 5)
      .forEach(item => {
        console.log(`  - ${item.name}: ${item.value.substring(0, 30)}...`);
      });
  }

  console.log('\n========================================');
  console.log('  ✅ 保存完成！');
  console.log('========================================');
  console.log(`\nCookies: ${COOKIES_FILE}`);
  console.log(`Storage: ${STORAGE_FILE}\n`);

  console.log('10秒后自动关闭浏览器...\n');
  await page.waitForTimeout(10000);

  await browser.close();
  console.log('✅ 浏览器已关闭\n');
}

fullSave().catch(error => {
  console.error('❌ 发生错误:', error.message);
  process.exit(1);
});
