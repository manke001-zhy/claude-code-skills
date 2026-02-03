/**
 * 百家号文章发布脚本
 * 支持登录状态缓存，自动发布文章
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 缓存目录
const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'baijiahao-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'baijiahao-storage.json');

async function publishArticle(articlePath) {
  console.log('========================================');
  console.log('  百家号文章发布助手');
  console.log('========================================\n');

  // 读取文章内容
  if (!fs.existsSync(articlePath)) {
    console.log(`❌ 文章文件不存在: ${articlePath}`);
    return;
  }

  const articleContent = fs.readFileSync(articlePath, 'utf-8');
  console.log(`✓ 已读取文章: ${path.basename(articlePath)}\n`);

  // 提取标题（第一行，去掉#号）
  const lines = articleContent.split('\n');
  let title = lines[0].replace(/^#+\s*/, '').trim();
  const body = articleContent.substring(articleContent.indexOf('\n') + 1);

  console.log(`标题: ${title}`);
  console.log(`内容长度: ${body.length} 字符\n`);

  // 检查是否有缓存
  const hasCookies = fs.existsSync(COOKIES_FILE);
  const hasStorage = fs.existsSync(STORAGE_FILE);

  if (!hasCookies && !hasStorage) {
    console.log('❌ 未找到登录状态缓存');
    console.log('请先运行: node baijiahao_full_save.cjs 保存登录状态\n');
    return;
  }

  console.log('[步骤 1] 启动浏览器...');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // 加载cookies
  if (hasCookies) {
    console.log('[步骤 2] 加载登录状态...');
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
      await context.addCookies(cookies);
      console.log('✓ Cookies已加载');
    } catch (error) {
      console.log('⚠️  Cookies加载失败');
    }
  }

  // 加载storage
  if (hasStorage) {
    try {
      const storage = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'));

      // 先访问页面
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
    } catch (error) {
      console.log('⚠️  Storage加载失败');
    }
  }

  console.log('[步骤 3] 访问百家号发布页面...');

  // 尝试访问发布页面
  try {
    await page.goto('https://baijiahao.baidu.com/builder/rc/edit', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    await page.waitForTimeout(3000);
  } catch (error) {
    console.log('⚠️  发布页面访问失败，尝试访问首页...');
    await page.goto('https://baijiahao.baidu.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    await page.waitForTimeout(3000);
  }

  // 检查登录状态
  const currentUrl = page.url();
  console.log(`当前页面: ${currentUrl}`);

  if (currentUrl.includes('login')) {
    console.log('\n⚠️  登录已失效');
    console.log('浏览器将保持打开，请手动登录后重试\n');
    console.log('[提示] 登录后请运行: node baijiahao_full_save.cjs\n');
    return;
  }

  console.log('[步骤 4] 查找文章发布入口...');

  // 尝试找到发布按钮或链接
  const publishEntry = await page.evaluate(() => {
    // 查找可能的发布入口
    const selectors = [
      'a[href*="edit"]',
      'a[href*="publish"]',
      'a[href*="post"]',
      'button[class*="publish"]',
      'button[class*="create"]',
      '[class*="write-btn"]',
      '[class*="publish-btn"]'
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        return {
          found: true,
          selector: selector,
          text: element.textContent?.trim(),
          href: element.href || ''
        };
      }
    }

    return { found: false };
  });

  if (publishEntry.found) {
    console.log(`✓ 找到发布入口: ${publishEntry.text || publishEntry.selector}`);

    // 如果是链接，点击进入
    if (publishEntry.href && !currentUrl.includes('edit')) {
      console.log('正在进入发布页面...');
      await page.goto(publishEntry.href);
      await page.waitForTimeout(3000);
    }
  } else {
    console.log('⚠️  未找到发布入口');
    console.log('可能需要手动点击发布按钮');
  }

  console.log('[步骤 5] 填写文章内容...');

  // 尝试多种方式填写标题和内容
  const fillResult = await page.evaluate((articleTitle, articleBody) => {
    // 查找标题输入框
    const titleSelectors = [
      'input[placeholder*="标题"]',
      'input[class*="title"]',
      'input[name="title"]',
      'input[id="title"]',
      '.title-input'
    ];

    let titleInput = null;
    for (const selector of titleSelectors) {
      const element = document.querySelector(selector);
      if (element && element.offsetParent !== null) {
        titleInput = element;
        break;
      }
    }

    // 查找内容输入框
    const bodySelectors = [
      'textarea[placeholder*="内容"]',
      'textarea[class*="content"]',
      'textarea[class*="body"]',
      'div[contenteditable="true"]',
      '.editor-content',
      '[class*="editor"]'
    ];

    let bodyInput = null;
    for (const selector of bodySelectors) {
      const element = document.querySelector(selector);
      if (element && element.offsetParent !== null) {
        bodyInput = element;
        break;
      }
    }

    const result = {
      titleFound: titleInput !== null,
      titleSelector: titleInput?.className || titleInput?.id || '',
      bodyFound: bodyInput !== null,
      bodySelector: bodyInput?.className || bodyInput?.id || ''
    };

    // 填写标题
    if (titleInput) {
      if (titleInput.tagName === 'INPUT') {
        titleInput.value = articleTitle;
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
        titleInput.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        titleInput.textContent = articleTitle;
      }
    }

    // 填写内容
    if (bodyInput) {
      if (bodyInput.tagName === 'TEXTAREA') {
        bodyInput.value = articleBody;
        bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
        bodyInput.dispatchEvent(new Event('change', { bubbles: true }));
      } else if (bodyInput.contentEditable === 'true') {
        bodyInput.textContent = articleBody;
        bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }

    return result;
  }, title, body);

  console.log(`标题输入框: ${fillResult.titleFound ? '✓' : '✗'}`);
  console.log(`内容输入框: ${fillResult.bodyFound ? '✓' : '✗'}`);

  if (!fillResult.titleFound || !fillResult.bodyFound) {
    console.log('\n⚠️  无法自动填写内容');
    console.log('浏览器将保持打开，请手动复制粘贴文章内容\n');

    // 将文章内容复制到剪贴板
    console.log('========== 文章内容（请手动复制）==========');
    console.log(`标题：${title}\n`);
    console.log(body);
    console.log('========================================\n');

    console.log('浏览器将在60秒后关闭，请尽快手动发布...');
    await page.waitForTimeout(60000);
    await browser.close();
    return;
  }

  console.log('[步骤 6] 查找发布按钮...');

  // 等待一下让输入生效
  await page.waitForTimeout(2000);

  // 查找发布按钮
  const publishButton = await page.evaluate(() => {
    const buttonSelectors = [
      'button:has-text("发布")',
      'button:has-text("提交")',
      'button:has-text("发表")',
      'a:has-text("发布")',
      '[class*="publish-btn"]',
      '[class*="submit-btn"]'
    ];

    for (const selector of buttonSelectors) {
      const element = document.querySelector(selector);
      if (element && element.offsetParent !== null) {
        return {
          found: true,
          text: element.textContent?.trim(),
          selector: selector
        };
      }
    }

    return { found: false };
  });

  if (publishButton.found) {
    console.log(`✓ 找到发布按钮: ${publishButton.text}`);
    console.log('\n请检查文章内容，确认无误后点击"发布"按钮');
    console.log('浏览器将保持打开30秒...\n');

    await page.waitForTimeout(30000);
  } else {
    console.log('⚠️  未找到发布按钮');
    console.log('请手动点击发布按钮');
    console.log('浏览器将保持打开60秒...\n');

    await page.waitForTimeout(60000);
  }

  console.log('========================================');
  console.log('  任务完成！');
  console.log('========================================\n');

  await browser.close();
}

// 获取文章路径
const articlePath = process.argv[2] || 'C:/Users/manke/Desktop/从微博热搜偷灵感.md';

publishArticle(articlePath).catch(error => {
  console.error('\n❌ 发生错误:', error.message);
  console.error(error.stack);
  process.exit(1);
});
