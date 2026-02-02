/**
 * 微博热搜榜高清截图 - 支持登录缓存
 * 首次登录后会保存cookies，下次无需重新登录
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const os = require('os');

// 保存到桌面
const desktopPath = path.join(os.homedir(), 'Desktop');
const OUTPUT_DIR = path.join(desktopPath, '微博热搜榜');

// Cookies缓存文件路径（指向dev-browser根目录）
const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'weibo-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'weibo-storage.json');

// 确保目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

async function main() {
  console.log('🚀 启动浏览器...');

  // 检查是否有缓存的登录状态
  const hasCache = fs.existsSync(COOKIES_FILE) && fs.existsSync(STORAGE_FILE);

  const browser = await chromium.launch({
    headless: false,
  });

  // 使用持久化上下文，保存用户数据
  const userDataDir = path.join(CACHE_DIR, 'user-data');
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    // 如果有缓存，加载cookies
    ...(hasCache ? {
      storageState: {
        cookies: JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8')),
        origins: JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'))
      }
    } : {})
  });

  const page = await context.newPage();

  // 先访问热搜榜页面
  console.log('🔥 正在前往微博热搜榜...');
  try {
    await page.goto('https://s.weibo.com/top/summary', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });
  } catch (error) {
    console.log('⚠️ 页面加载超时，尝试继续...');
  }

  await page.waitForTimeout(3000);

  // 检查是否需要登录
  const needLogin = await page.evaluate(() => {
    // 检查页面是否显示登录框或跳转到登录页
    const url = window.location.href;
    return url.includes('login') ||
           url.includes('signup') ||
           document.querySelector('.login_btn') !== null ||
           document.body.textContent.includes('登录') ||
           document.querySelector('#pl_top_realtimehot table tbody tr') === null;
  });

  if (needLogin) {
    console.log('');
    console.log('='.repeat(60));
    console.log('⚠️  需要登录微博');
    console.log('   请在浏览器中扫码登录...');
    console.log('='.repeat(60));
    console.log('');

    // 跳转到登录页
    await page.goto('https://weibo.com/newlogin', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    // 等待登录成功
    let isLoggedIn = false;
    const maxWaitTime = 120000;
    const checkInterval = 2000;
    let elapsedTime = 0;

    while (!isLoggedIn && elapsedTime < maxWaitTime) {
      await page.waitForTimeout(checkInterval);
      elapsedTime += checkInterval;

      const currentUrl = page.url();
      if (!currentUrl.includes('login') &&
          !currentUrl.includes('signup') &&
          !currentUrl.includes('visitor')) {
        isLoggedIn = true;
      }

      if (elapsedTime % 10000 === 0) {
        console.log(`⏳ 等待登录中... (${elapsedTime/1000}秒)`);
      }
    }

    if (!isLoggedIn) {
      console.log('❌ 登录超时');
      await browser.close();
      return;
    }

    console.log('✅ 登录成功！正在保存登录状态...');

    // 保存cookies和storage状态
    const cookies = await context.cookies();
    const storageState = await context.storageState();

    fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');
    fs.writeFileSync(STORAGE_FILE, JSON.stringify(storageState.origins || [], null, 2), 'utf-8');

    console.log('✅ 登录状态已保存，下次无需重新登录');

    await page.waitForTimeout(2000);

    // 重新访问热搜榜
    console.log('🔥 正在前往微博热搜榜...');
    try {
      await page.goto('https://s.weibo.com/top/summary', {
        waitUntil: 'domcontentloaded',
        timeout: 60000
      });
    } catch (error) {
      console.log('⚠️ 页面加载超时，尝试继续...');
    }
    await page.waitForTimeout(3000);
  } else {
    console.log('✅ 已登录，无需重新登录');
  }

  // 截取完整的热搜榜页面
  console.log('📸 正在截取高清热搜榜...');
  const screenshotPath = path.join(OUTPUT_DIR, `热搜榜_高清_${new Date().toLocaleString('zh-CN').replace(/[\/\s:]/g, '-')}.png`);
  await page.screenshot({
    path: screenshotPath,
    fullPage: true,
    type: 'png'
  });

  console.log('✅ 截图已保存:', screenshotPath);
  console.log('');
  console.log('='.repeat(60));
  console.log('✅ 完成！高清截图已保存到桌面');
  console.log('='.repeat(60));

  await page.waitForTimeout(3000);
  await browser.close();
}

main().catch(console.error);
