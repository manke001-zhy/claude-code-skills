/**
 * 微博发帖助手 v2
 * 支持登录缓存，智能查找发布按钮
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 缓存目录
const CACHE_DIR = path.join(__dirname, '../../.cache');
const COOKIES_FILE = path.join(CACHE_DIR, 'weibo-cookies.json');
const STORAGE_FILE = path.join(CACHE_DIR, 'weibo-storage.json');

// 确保目录存在
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

async function postWeibo(content) {
  if (!content) {
    console.error('❌ 请提供要发布的内容');
    console.log('\n使用方法：');
    console.log('  node weibo_post.cjs "微博内容"');
    console.log('\n示例：');
    console.log('  node weibo_post.cjs "今天天气真好！"');
    process.exit(1);
  }

  console.log('========================================');
  console.log('  微博发帖助手 v2');
  console.log('========================================\n');
  console.log(`发布内容: ${content}\n`);

  // 检查是否有缓存
  const hasCache = fs.existsSync(COOKIES_FILE) && fs.existsSync(STORAGE_FILE);

  let browser;
  try {
    console.log('[步骤 1] 启动浏览器...');
    browser = await chromium.launch({
      headless: false,
      slowMo: 100
    });

    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });

    const page = await context.newPage();

    // 如果有缓存，加载cookies
    if (hasCache) {
      console.log('[步骤 2] 加载已保存的登录状态...');
      try {
        const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
        const storage = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'));

        await context.addCookies(cookies);

        // 添加localStorage
        if (storage && storage.length > 0) {
          await page.goto('https://weibo.com', { waitUntil: 'domcontentloaded' });
          await page.evaluate((storage) => {
            storage.forEach(item => {
              if (item.origin && item.localStorage) {
                item.localStorage.forEach(({ name, value }) => {
                  localStorage.setItem(name, value);
                });
              }
            });
          }, storage);
        }

        console.log('✓ 已加载缓存\n');
      } catch (error) {
        console.log('⚠️  缓存加载失败，需要重新登录\n');
      }
    } else {
      console.log('[步骤 2] 未找到缓存，需要登录\n');
    }

    console.log('[步骤 3] 打开微博首页...');
    await page.goto('https://weibo.com', {
      waitUntil: 'domcontentloaded'
    });
    await page.waitForTimeout(3000);

    // 检查是否已登录
    const isLoggedIn = await page.evaluate(() => {
      const avatar = document.querySelector('[class*="avatar"]') ||
                     document.querySelector('[class*="user"]');
      return avatar !== null;
    });

    if (!isLoggedIn) {
      console.log('\n========================================');
      console.log('  ⏳ 请先登录微博');
      console.log('========================================\n');
      console.log('请在浏览器中完成登录...');
      console.log('登录成功后脚本会继续\n');

      // 等待登录
      let loginSuccess = false;
      for (let i = 0; i < 60; i++) {
        await page.waitForTimeout(5000);
        const checkLogin = await page.evaluate(() => {
          const avatar = document.querySelector('[class*="avatar"]') ||
                         document.querySelector('[class*="user"]');
          return avatar !== null;
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
        throw new Error('登录超时');
      }

      console.log('\n✅ 登录成功！');

      // 保存登录状态
      await page.waitForTimeout(2000);
      const cookies = await context.cookies();
      fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2), 'utf-8');

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
        origin: 'https://weibo.com',
        localStorage: localStorage
      }];
      fs.writeFileSync(STORAGE_FILE, JSON.stringify(storageData, null, 2), 'utf-8');

      console.log('✓ 登录状态已保存\n');
    } else {
      console.log('✓ 已登录\n');
    }

    console.log('[步骤 4] 查找发布框...');

    // 等待页面完全加载
    await page.waitForTimeout(2000);

    // 使用JavaScript查找发布框和按钮
    const pageInfo = await page.evaluate(() => {
      let textarea = null;
      let textareaSelector = null;

      // 查找发布框
      const textareaSelectors = [
        'textarea[placeholder*="有什么新鲜事"]',
        'textarea[placeholder*="分享你的想法"]',
        '.WB_textarea',
        'textarea[class*="publish"]',
        'textarea[class*="send"]',
        '#texta',
        'textarea[node-type="text"]',
        'textarea'
      ];

      for (const selector of textareaSelectors) {
        try {
          const element = document.querySelector(selector);
          if (element && element.offsetParent !== null) {
            textarea = element;
            textareaSelector = selector;
            break;
          }
        } catch (e) {}
      }

      return {
        textareaSelector,
        textareaPlaceholder: textarea?.placeholder || null,
        textareaClass: textarea?.className || null,
        allTextareas: Array.from(document.querySelectorAll('textarea')).map(t => ({
          placeholder: t.placeholder,
          className: t.className,
          id: t.id
        }))
      };
    });

    console.log(`页面信息: ${JSON.stringify(pageInfo, null, 2)}`);

    let publishBox;
    if (pageInfo.textareaSelector) {
      publishBox = await page.$(pageInfo.textareaSelector);
      console.log(`✓ 找到发布框 (${pageInfo.textareaSelector})`);
    } else {
      // 使用第一个可见的textarea
      const allTextareas = await page.$$('textarea');
      console.log(`找到 ${allTextareas.length} 个文本框`);

      for (const textarea of allTextareas) {
        const isVisible = await textarea.isIntersectingViewport();
        if (isVisible) {
          publishBox = textarea;
          console.log('✓ 使用第一个可见文本框');
          break;
        }
      }
    }

    if (!publishBox) {
      throw new Error('未找到发布框');
    }

    console.log('\n[步骤 5] 输入内容...');

    // 点击发布框并输入
    await publishBox.click();
    await page.waitForTimeout(300);

    // 清空并输入
    await publishBox.fill('');
    await page.waitForTimeout(200);

    // 逐字输入
    await publishBox.type(content, { delay: 50 });
    await page.waitForTimeout(500);

    console.log('✓ 内容已输入');

    console.log('\n[步骤 6] 查找发布按钮...');

    // 等待按钮出现
    await page.waitForTimeout(1000);

    // 使用JavaScript智能查找发布按钮
    const buttonInfo = await page.evaluate(() => {
      const buttons = [];

      // 查找所有可能包含"发布"的元素
      const allElements = document.querySelectorAll('a, button, span, div[role="button"]');

      allElements.forEach(el => {
        const text = el.textContent?.trim() || '';
        const className = el.className || '';
        const attrs = {};

        // 检查常用属性
        ['action-type', 'node-type', 'data-action', 'role'].forEach(attr => {
          const value = el.getAttribute(attr);
          if (value) attrs[attr] = value;
        });

        // 查找包含"发布"、"發布"、"发送"、"提交"等关键词的元素
        if (
          text.includes('发布') ||
          text.includes('發布') ||
          text.includes('发送') ||
          text.includes('提交') ||
          text === '發佈' ||
          text === 'Pub' ||
          text === 'Post' ||
          text === 'Send' ||
          className.includes('publish') ||
          className.includes('submit') ||
          attrs['action-type'] === 'doPublish' ||
          attrs['node-type'] === 'publishBtn'
        ) {
          // 检查元素是否可见
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();

          if (style.display !== 'none' &&
              style.visibility !== 'hidden' &&
              rect.width > 0 &&
              rect.height > 0) {
            buttons.push({
              text: text.substring(0, 30),
              className: className.substring(0, 50),
              attrs,
              tagName: el.tagName,
              id: el.id
            });
          }
        }
      });

      return buttons;
    });

    console.log(`找到 ${buttonInfo.length} 个可能的发布按钮:`);
    buttonInfo.forEach((btn, i) => {
      console.log(`  ${i + 1}. [${btn.tagName}] "${btn.text}" (class: ${btn.className.substring(0, 30)})`);
    });

    if (buttonInfo.length === 0) {
      console.log('\n⚠️  未找到发布按钮');
      console.log('内容已输入，请手动点击发布按钮');
      console.log('\n浏览器将保持打开30秒...\n');
      await page.waitForTimeout(30000);
      await browser.close();
      return;
    }

    // 选择最佳按钮（优先选择文本完全匹配"发布"的）
    let bestButton = buttonInfo.find(btn =>
      btn.text === '发布' || btn.text === '發布' || btn.text === '发送'
    ) || buttonInfo[0];

    console.log(`\n选择按钮: [${bestButton.tagName}] "${bestButton.text}"`);

    // 使用JavaScript直接点击
    console.log('\n[步骤 7] 点击发布按钮...');

    const clickSuccess = await page.evaluate((buttonInfo) => {
      // 根据按钮信息查找并点击
      const allElements = document.querySelectorAll('a, button, span, div[role="button"]');

      for (const el of allElements) {
        const text = el.textContent?.trim() || '';
        const className = el.className || '';

        // 匹配按钮
        if (
          text === buttonInfo.text &&
          className.includes(buttonInfo.className.substring(0, 20))
        ) {
          // 点击
          el.click();
          return true;
        }
      }

      return false;
    }, bestButton);

    if (clickSuccess) {
      console.log('✓ 已点击发布按钮');
    } else {
      // 如果JavaScript点击失败，尝试使用Playwright点击
      try {
        const selector = `text="${bestButton.text}"`;
        const element = await page.locator(selector).first();
        await element.click({ timeout: 5000 });
        console.log('✓ 已点击发布按钮（使用Playwright）');
      } catch (e) {
        console.log('⚠️  点击失败，请手动点击发布按钮');
        console.log('\n浏览器将保持打开30秒...\n');
        await page.waitForTimeout(30000);
        await browser.close();
        return;
      }
    }

    console.log('\n等待发布完成...');
    await page.waitForTimeout(5000);

    console.log('\n========================================');
    console.log('  ✅ 微博发布完成！');
    console.log('========================================\n');
    console.log(`发布内容: ${content}\n`);

    console.log('浏览器将在 3 秒后关闭...');
    await page.waitForTimeout(3000);

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
    console.error(error.stack);
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n程序结束');
    }
  }
}

// 运行
const content = process.argv[2];
postWeibo(content).catch(console.error);
