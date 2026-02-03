/**
 * 百家号数据查看脚本 - 支持登录状态缓存
 * 查看阅读量、收益、粉丝数等数据
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 缓存目录
const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'baijiahao-storage.json');

async function viewData() {
  console.log('========================================');
  console.log('  百家号数据查看');
  console.log('========================================\n');

  // 检查是否有缓存的登录状态
  const hasCache = fs.existsSync(COOKIES_FILE);

  const browser = await chromium.launch({
    headless: false,  // 显示浏览器，方便查看
    slowMo: 100
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // 如果有缓存，加载cookies和storage
  const hasCookies = fs.existsSync(COOKIES_FILE);
  const hasStorage = fs.existsSync(STORAGE_FILE);

  if (hasCookies) {
    console.log('[步骤 1] 加载已保存的登录状态...');
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
      await context.addCookies(cookies);
      console.log('✓ Cookies已加载');
    } catch (error) {
      console.log('⚠️  Cookies加载失败');
    }
  }

  if (hasStorage) {
    try {
      const storage = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'));

      // 先访问页面以设置origin
      await page.goto('https://baijiahao.baidu.com/', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });

      // 加载localStorage
      if (storage.localStorage && storage.localStorage.length > 0) {
        await page.evaluate((storageData) => {
          storageData.forEach(({ name, value }) => {
            localStorage.setItem(name, value);
          });
        }, storage.localStorage);
        console.log('✓ LocalStorage已加载');
      }

      // 加载sessionStorage
      if (storage.sessionStorage && storage.sessionStorage.length > 0) {
        await page.evaluate((storageData) => {
          storageData.forEach(({ name, value }) => {
            sessionStorage.setItem(name, value);
          });
        }, storage.sessionStorage);
        console.log('✓ SessionStorage已加载');
      }
    } catch (error) {
      console.log('⚠️  Storage加载失败');
    }
  }

  if (!hasCookies && !hasStorage) {
    console.log('\n⚠️  未找到缓存，需要先登录');
    console.log('提示：请先运行 baijiahao_full_save.cjs 保存登录状态\n');
    await browser.close();
    return;
  }

  console.log(''); // 换行

  console.log('[步骤 2] 访问百家号数据页面...');

  // 访问百家号后台首页
  try {
    await page.goto('https://baijiahao.baidu.com/builder/rc/dashboard', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    await page.waitForTimeout(3000);
  } catch (error) {
    console.log('⚠️  后台页面访问失败，尝试访问首页...');
    await page.goto('https://baijiahao.baidu.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    await page.waitForTimeout(3000);
  }

  // 检查当前页面状态
  const currentUrl = page.url();
  console.log(`当前页面: ${currentUrl}`);

  const needLogin = await page.evaluate(() => {
    return window.location.href.includes('login') ||
           document.querySelector('.login-btn') !== null;
  });

  if (needLogin) {
    console.log('\n⚠️  检测到登录页面');
    console.log('但浏览器会保持打开，你可以手动登录');
    console.log('登录后数据会显示在页面上\n');
    // 不关闭浏览器，让用户手动查看
  } else {
    console.log('✓ 已登录或可访问页面\n');
  }

  console.log('[步骤 3] 提取数据...\n');

  // 尝试多种方式提取数据
  const data = await page.evaluate(() => {
    const result = {
      pageUrl: window.location.href,
      pageTitle: document.title,
      rawData: {}
    };

    // 尝试查找常见的数值展示元素
    const numberSelectors = [
      '.num', '.count', '.data-num', '.read-count',
      '.view-count', '.fans-count', '.income-num',
      '[class*="num"]', '[class*="count"]', '[class*="data"]'
    ];

    numberSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((el, index) => {
        const text = el.textContent?.trim();
        const parent = el.parentElement?.textContent?.trim();
        if (text && /^\d+/.test(text)) {
          result.rawData[`${selector}_${index}`] = {
            value: text,
            context: parent?.substring(0, 50) || ''
          };
        }
      });
    });

    // 查找卡片数据
    const cards = document.querySelectorAll('.card, .data-card, .stat-card, [class*="card"]');
    cards.forEach((card, index) => {
      const cardText = card.textContent?.trim();
      if (cardText && cardText.length < 200) {
        result.rawData[`card_${index}`] = cardText;
      }
    });

    // 获取页面主体文本
    const mainContent = document.querySelector('main, .main, [class*="main"]')?.textContent?.trim();
    if (mainContent) {
      result.mainContentPreview = mainContent.substring(0, 500);
    }

    return result;
  });

  // 显示提取的数据
  console.log('📊 页面信息:');
  console.log(`  标题: ${data.pageTitle}`);
  console.log(`  URL: ${data.pageUrl}\n`);

  console.log('📈 数据预览:');
  console.log('----------------------------------------');

  const entries = Object.entries(data.rawData);
  if (entries.length > 0) {
    // 只显示前15条数据，避免输出太多
    entries.slice(0, 15).forEach(([key, value]) => {
      if (typeof value === 'object') {
        console.log(`  ${key}:`);
        console.log(`    值: ${value.value}`);
        if (value.context) {
          console.log(`    上下文: ${value.context.substring(0, 40)}...`);
        }
      } else {
        console.log(`  ${key}: ${value.substring(0, 80)}`);
      }
      console.log('');
    });

    if (entries.length > 15) {
      console.log(`  ... 还有 ${entries.length - 15} 条数据\n`);
    }
  } else {
    console.log('  未提取到结构化数据');
    console.log('  页面可能需要手动查看\n');
  }

  if (data.mainContentPreview) {
    console.log('📄 页面内容预览:');
    console.log('----------------------------------------');
    console.log(data.mainContentPreview);
    console.log('----------------------------------------\n');
  }

  // 保存完整数据到JSON文件
  const outputFile = path.join(__dirname, 'baijiahao_data.json');
  fs.writeFileSync(outputFile, JSON.stringify(data, null, 2), 'utf-8');
  console.log(`✅ 完整数据已保存到: ${outputFile}\n`);

  console.log('========================================');
  console.log('  浏览器将保持打开，你可以手动查看详细数据');
  console.log('  按 Ctrl+C 关闭浏览器');
  console.log('========================================\n');

  // 保持浏览器打开
  await new Promise(() => {});
}

viewData().catch(error => {
  console.error('❌ 发生错误:', error.message);
  console.error(error.stack);
  process.exit(1);
});
