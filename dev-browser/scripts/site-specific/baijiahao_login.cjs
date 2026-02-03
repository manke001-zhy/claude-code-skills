/**
 * 百家号登录脚本 - 支持登录状态缓存
 * 首次登录后保存cookies，后续自动复用
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 缓存目录
const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'baijiahao-storage.json');

// 确保缓存目录存在
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

async function main() {
  console.log('========================================');
  console.log('  百家号登录助手');
  console.log('========================================\n');

  // 检查是否有缓存
  const hasCache = fs.existsSync(COOKIES_FILE) && fs.existsSync(STORAGE_FILE);

  const browser = await chromium.launch({
    headless: false,  // 显示浏览器窗口
    slowMo: 100
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // 如果有缓存，加载cookies
  if (hasCache) {
    console.log('[步骤 1] 加载已保存的登录状态...\n');
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
      await context.addCookies(cookies);
      console.log('✓ 已加载缓存\n');
    } catch (error) {
      console.log('⚠️  缓存加载失败，需要重新登录\n');
    }
  } else {
    console.log('[步骤 1] 未找到缓存，需要登录\n');
  }

  console.log('[步骤 2] 打开百家号首页...');
  await page.goto('https://baijiahao.baidu.com/', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  await page.waitForTimeout(3000);

  // 检查是否已登录
  const isLoggedIn = await page.evaluate(() => {
    // 百家号登录后的特征元素
    const userAvatar = document.querySelector('[class*="avatar"]') ||
                      document.querySelector('[class*="user"]') ||
                      document.querySelector('.user-info') ||
                      document.querySelector('[data-module="userCenter"]');
    return userAvatar !== null;
  });

  if (!isLoggedIn) {
    console.log('\n========================================');
    console.log('  ⏳ 请先登录百家号');
    console.log('========================================\n');
    console.log('请在浏览器中完成登录...');
    console.log('登录成功后脚本会自动检测并保存登录状态\n');

    // 等待登录（最多等待2分钟）
    let loginSuccess = false;
    for (let i = 0; i < 24; i++) {
      await page.waitForTimeout(5000);

      const checkLogin = await page.evaluate(() => {
        const userAvatar = document.querySelector('[class*="avatar"]') ||
                          document.querySelector('[class*="user"]') ||
                          document.querySelector('.user-info') ||
                          document.querySelector('[data-module="userCenter"]');
        return userAvatar !== null;
      });

      if (checkLogin) {
        loginSuccess = true;
        break;
      }

      if (i % 6 === 0) {
        console.log(`等待登录中... ${i * 5}秒`);
      }
    }

    if (!loginSuccess) {
      console.log('\n❌ 登录超时');
      await browser.close();
      return;
    }

    console.log('\n✅ 登录成功！');

    // 保存登录状态
    await page.waitForTimeout(2000);
    const cookies = await context.cookies();
    fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');

    // 尝试保存localStorage（如果有的话）
    try {
      const localStorage = await page.evaluate(() => {
        const storage = [];
        for (let i = 0; i < localStorage.length; i++) {
          const name = localStorage.key(i);
          const value = localStorage.getItem(name);
          storage.push({ name, value });
        }
        return storage;
      });

      const storageData = [{
        origin: 'https://baijiahao.baidu.com',
        localStorage: localStorage
      }];
      fs.writeFileSync(STORAGE_FILE, JSON.stringify(storageData, null, 2), 'utf-8');
    } catch (e) {
      // localStorage保存失败不影响cookies保存
    }

    console.log('✓ 登录状态已保存（下次将自动登录）\n');
  } else {
    console.log('✓ 已登录（使用缓存的登录状态）\n');
  }

  console.log('[步骤 3] 获取用户信息...');

  try {
    const userInfo = await page.evaluate(() => {
      // 尝试获取用户信息
      const avatar = document.querySelector('[class*="avatar"]');
      const userName = document.querySelector('[class*="user-name"]') ||
                      document.querySelector('.user-name') ||
                      document.querySelector('[data-module="userCenter"]');

      return {
        hasAvatar: !!avatar,
        hasUserCenter: !!userName,
        pageTitle: document.title,
        pageURL: window.location.href
      };
    });

    console.log('页面信息:');
    console.log(`  - 标题: ${userInfo.pageTitle}`);
    console.log(`  - URL: ${userInfo.pageURL}`);
    console.log(`  - 已登录: ${userInfo.hasUserCenter ? '是' : '否'}\n`);

  } catch (e) {
    console.log('⚠️  无法获取用户信息\n');
  }

  console.log('========================================');
  console.log('  ✅ 百家号登录完成！');
  console.log('========================================\n');
  console.log('浏览器将保持打开，你可以继续操作百家号');
  console.log('按 Ctrl+C 关闭浏览器\n');

  // 保持浏览器打开，直到用户主动关闭
  await new Promise(() => {});  // 永不resolve，保持运行
}

main().catch(error => {
  console.error('❌ 发生错误:', error.message);
  process.exit(1);
});
