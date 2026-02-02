#!/usr/bin/env node

/**
 * 使用已保存的百度会话进行搜索
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sessionFile = path.join(__dirname, '../../sessions/session_www_baidu_com.json');

async function searchAndOpen(keyword) {
  if (!keyword) {
    console.error('请提供搜索关键词');
    process.exit(1);
  }

  console.log('========================================');
  console.log('  百度搜索助手');
  console.log('========================================\n');
  console.log(`搜索关键词: ${keyword}\n`);

  // 检查会话文件
  if (!fs.existsSync(sessionFile)) {
    console.error('❌ 未找到百度登录会话，请先运行：');
    console.log('   node universal_login.js https://www.baidu.com\n');
    process.exit(1);
  }

  console.log('[步骤 1] 加载已保存的登录会话...');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 300
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    storageState: sessionFile
  });

  const page = await context.newPage();

  try {
    console.log('[步骤 2] 打开百度...');
    await page.goto('https://www.baidu.com', {
      waitUntil: 'domcontentloaded'
    });

    // 等待页面稳定
    await page.waitForTimeout(2000);

    // 检查登录状态
    const isLoggedIn = await page.evaluate(() => {
      const avatar = document.querySelector('[class*="profile"], [class*="avatar"], [class*="user"]');
      return avatar !== null;
    });

    if (!isLoggedIn) {
      console.log('\n⚠️  会话可能已失效，尝试继续搜索...\n');
    } else {
      console.log('✓ 登录状态正常\n');
    }

    console.log(`[步骤 3] 搜索 "${keyword}"...`);

    // 尝试多种方式找到搜索框
    let searchBox = null;

    // 方法1: 通过ID查找
    try {
      const element = await page.$('#kw');
      if (element) {
        searchBox = element;
        console.log('✓ 通过 #kw 找到搜索框');
      }
    } catch (e) {}

    // 方法2: 通过name属性
    if (!searchBox) {
      try {
        const element = await page.$('input[name="wd"]');
        if (element) {
          searchBox = element;
          console.log('✓通过 name="wd" 找到搜索框');
        }
      } catch (e) {}
    }

    // 方法3: 通过class查找
    if (!searchBox) {
      try {
        const element = await page.$('.s_ipt');
        if (element) {
          searchBox = element;
          console.log('✓ 通过 .s_ipt 找到搜索框');
        }
      } catch (e) {}
    }

    // 方法4: 查找所有输入框
    if (!searchBox) {
      const allInputs = await page.$$('input[type="text"]');
      console.log(`找到 ${allInputs.length} 个文本输入框`);
      for (const input of allInputs) {
        const placeholder = await input.getAttribute('placeholder');
        const id = await input.getAttribute('id');
        const name = await input.getAttribute('name');
        console.log(`  - id="${id}" name="${name}" placeholder="${placeholder}"`);

        // 选择第一个看起来像搜索框的
        if (!searchBox && (id === 'kw' || name === 'wd' || placeholder?.includes('百度'))) {
          searchBox = input;
        }
      }

      // 如果还没找到，用第一个输入框
      if (!searchBox && allInputs.length > 0) {
        searchBox = allInputs[0];
        console.log('✓ 使用第一个文本输入框');
      }
    }

    if (!searchBox) {
      throw new Error('未找到搜索框');
    }

    // 输入搜索关键词 - 使用JavaScript直接操作
    console.log('正在输入搜索关键词...');
    await page.evaluate((keyword) => {
      const searchBox = document.querySelector('#kw');
      if (searchBox) {
        searchBox.focus();
        searchBox.value = keyword;
        // 触发input事件
        const event = new Event('input', { bubbles: true });
        searchBox.dispatchEvent(event);
      }
    }, keyword);
    await page.waitForTimeout(500);

    // 查找搜索按钮并点击
    console.log('\n查找搜索按钮...');

    let clicked = false;

    // 尝试点击按钮
    const buttonSelectors = [
      '#su',
      'input[value="百度一下"]',
      '.s_btn',
      'button[type="submit"]'
    ];

    for (const selector of buttonSelectors) {
      try {
        const button = await page.$(selector);
        if (button) {
          await button.click();
          console.log(`✓ 点击搜索按钮 (${selector})`);
          clicked = true;
          break;
        }
      } catch (e) {}
    }

    // 如果没找到按钮，按回车
    if (!clicked) {
      console.log('未找到按钮，尝试按回车...');
      await searchBox.press('Enter');
      console.log('✓ 已按回车键');
    }

    console.log('\n[步骤 4] 等待搜索结果加载...');
    await page.waitForTimeout(3000);

    console.log('\n[步骤 5] 查找第一个搜索结果...');

    // 尝试找到第一个搜索结果链接
    const resultFound = await page.evaluate(() => {
      // 尝试多种选择器
      const selectors = [
        '.result a',
        '#content_left .c-container a',
        'div[tpl="se_com_default"] a',
        '.t a',
        'h3 a'
      ];

      for (const selector of selectors) {
        const links = document.querySelectorAll(selector);
        if (links.length > 0) {
          return {
            found: true,
            text: links[0].textContent,
            href: links[0].href
          };
        }
      }

      return { found: false };
    });

    if (resultFound.found) {
      console.log(`✓ 找到结果: ${resultFound.text.substring(0, 50)}...`);
      console.log(`  链接: ${resultFound.href.substring(0, 80)}...`);

      console.log('\n[步骤 6] 打开搜索结果...');
      await page.goto(resultFound.href, {
        waitUntil: 'domcontentloaded'
      });

      await page.waitForTimeout(2000);

      const currentUrl = page.url();
      const currentTitle = await page.title();

      console.log('\n========================================');
      console.log('  ✅ 已打开！');
      console.log('========================================\n');
      console.log(`页面标题: ${currentTitle}`);
      console.log(`页面URL: ${currentUrl}\n`);

      console.log('浏览器将保持打开，您可以继续操作...');
      console.log('按 Ctrl+C 或关闭窗口结束\n');

      // 保持浏览器打开
      await new Promise(() => {});

    } else {
      console.log('\n⚠️  未找到搜索结果');
      console.log('浏览器将保持打开以便查看...\n');

      // 保持浏览器打开
      await new Promise(() => {});
    }

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
    console.error(error.stack);
    await browser.close();
  }
}

// 运行
const keyword = process.argv[2] || '微博';
searchAndOpen(keyword).catch(console.error);
