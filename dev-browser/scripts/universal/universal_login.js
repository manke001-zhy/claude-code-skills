#!/usr/bin/env node

/**
 * 通用网站登录助手
 * 支持任意网站的登录状态保存和自动复用
 *
 * 使用方法：
 *   node universal_login.js https://example.com
 *   node universal_login.js https://example.com --session-name mysite
 *
 * 功能：
 * - 自动检测并保存登录状态
 * - 下次自动加载已保存的会话
 * - 支持会话过期自动重新登录
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 从URL提取域名作为会话文件名
function getDomainFromUrl(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace(/\./g, '_');
  } catch {
    return 'website';
  }
}

// 多种方法检测登录状态
async function checkLoginStatus(page, context) {
  const results = {
    hasCookies: false,
    hasAvatar: false,
    isLoggedIn: false,
    details: []
  };

  // 方法1: 检查cookies
  const cookies = await context.cookies();
  const hasAuthCookies = cookies.some(c =>
    c.name.includes('session') ||
    c.name.includes('token') ||
    c.name.includes('auth') ||
    c.name === 'z_c0' ||
    c.name === 'd_c0' ||
    c.name === 'tst'
  );
  results.hasCookies = hasAuthCookies || cookies.length > 3;
  results.details.push(`Cookies: ${results.hasCookies ? '✓' : '✗'} (${cookies.length}个)`);

  // 方法2: 检查常见的登录后元素
  const hasLoggedInElements = await page.evaluate(() => {
    const selectors = [
      // 通用选择器
      '[class*="profile"]',
      '[class*="avatar"]',
      '[class*="user"]',
      '[id*="profile"]',
      '[id*="avatar"]',
      '[class*="logout"]',
      // 用户头像img
      'img[src*="avatar"]',
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        // 检查是否可见
        const style = window.getComputedStyle(element);
        if (style.display !== 'none' && style.visibility !== 'hidden') {
          return true;
        }
      }
    }

    // 检查是否有退出/登出按钮
    const allButtons = document.querySelectorAll('button, a');
    for (const btn of allButtons) {
      const text = btn.textContent || '';
      if (text.includes('退出') || text.includes('登出') || text.includes('Logout')) {
        return true;
      }
    }

    return false;
  });
  results.hasAvatar = hasLoggedInElements;
  results.details.push(`登录元素: ${hasLoggedInElements ? '✓' : '✗'}`);

  // 方法3: 检查是否在登录页面
  const currentUrl = page.url();
  const isLoginPage = currentUrl.includes('login') ||
                      currentUrl.includes('signin') ||
                      currentUrl.includes('auth');
  results.details.push(`URL检查: ${!isLoginPage ? '✓' : '✗'}`);

  // 方法4: 检查是否有登录按钮（有登录按钮说明未登录）
  const hasLoginButton = await page.evaluate(() => {
    const selectors = [
      '.login',
      '.signin',
      '[class*="login-btn"]',
      '[id*="login"]',
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        const style = window.getComputedStyle(element);
        if (style.display !== 'none' && style.visibility !== 'hidden') {
          return true;
        }
      }
    }

    // 检查是否有登录/注册文本的按钮
    const allButtons = document.querySelectorAll('button, a');
    for (const btn of allButtons) {
      const text = btn.textContent || '';
      if ((text.includes('登录') || text.includes('注册') || text.includes('Login') || text.includes('Sign in')) && text.length < 20) {
        return true;
      }
    }

    return false;
  });
  results.details.push(`登录按钮: ${hasLoginButton ? '✓ (未登录)' : '✗ (已登录)'}`);

  // 综合判断
  // 已登录条件：有cookies + (有头像 或 没有登录按钮 且 不在登录页面)
  results.isLoggedIn = results.hasCookies &&
                       (results.hasAvatar || (!hasLoginButton && !isLoginPage));

  return results;
}

// 主函数
async function universalLogin(targetUrl, sessionName = null) {
  if (!targetUrl) {
    console.error('错误：请提供网站URL');
    console.log('\n使用方法：');
    console.log('  node universal_login.js <网站URL>');
    console.log('  node universal_login.js <网站URL> --session-name <会话名称>\n');
    console.log('示例：');
    console.log('  node universal_login.js https://www.zhihu.com');
    console.log('  node universal_login.js https://github.com --session-name github');
    process.exit(1);
  }

  // 确定会话文件名
  const domain = sessionName || getDomainFromUrl(targetUrl);
  const sessionFile = path.join(__dirname, '../../sessions', `session_${domain}.json`);

  console.log('========================================');
  console.log('  通用网站登录助手');
  console.log('========================================\n');
  console.log(`目标网站: ${targetUrl}`);
  console.log(`会话文件: session_${domain}.json\n`);

  // 检查是否已有会话
  let useExistingSession = false;
  let sessionAge = 0;

  if (fs.existsSync(sessionFile)) {
    const stats = fs.statSync(sessionFile);
    sessionAge = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60 * 24); // 天数
    console.log(`[会话检查] 发现已保存的登录状态 (${sessionAge.toFixed(1)}天前)`);

    // 如果会话未超过7天，自动使用
    if (sessionAge < 7) {
      console.log('自动选择：使用已保存会话（未超过7天）\n');
      useExistingSession = true;
    } else {
      console.log('提示：会话已超过7天，建议重新登录\n');
    }
  }

  // 启动浏览器
  const browser = await chromium.launch({
    headless: false,
    slowMo: 200
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    storageState: useExistingSession ? sessionFile : undefined
  });

  const page = await context.newPage();

  try {
    console.log('[步骤 1] 打开网站...');
    await page.goto(targetUrl, {
      waitUntil: 'domcontentloaded'
    });

    console.log('[步骤 2] 检测登录状态...\n');

    const status = await checkLoginStatus(page, context);
    status.details.forEach(detail => console.log(`  ${detail}`));

    if (status.isLoggedIn && useExistingSession) {
      console.log('\n✅ 检测到已登录状态！');
      console.log('使用已保存的会话，无需重新登录！\n');

      console.log('浏览器将在 5 秒后关闭...');
      await page.waitForTimeout(5000);
      await browser.close();
      console.log('\n✅ 完成！');
      return;
    }

    if (useExistingSession && !status.isLoggedIn) {
      console.log('\n⚠️  已保存的会话已失效，需要重新登录\n');
    }

    if (!status.isLoggedIn) {
      console.log('[步骤 3] 查找登录入口...');

      // 尝试自动点击登录按钮
      const loginSelectors = [
        'text=登录',
        'text=注册/登录',
        'text=Sign in',
        'text=Log in',
        '.login',
        '.signin',
        '.login-btn',
        '.sign-in-btn',
        'button:has-text("登录")',
        'a:has-text("登录")',
        'button:has-text("Sign in")',
        'a:has-text("Sign in")',
      ];

      let clicked = false;
      for (const selector of loginSelectors) {
        try {
          const element = await page.locator(selector).first();
          if (await element.isVisible({ timeout: 1000 })) {
            await element.click();
            console.log(`✓ 点击登录按钮 (${selector})`);
            clicked = true;
            await page.waitForTimeout(1000);
            break;
          }
        } catch (e) {
          // 继续尝试下一个
        }
      }

      if (!clicked) {
        console.log('提示：未找到登录按钮，可能已在登录页面');
      }

      console.log('\n========================================');
      console.log('  ⏳ 请在浏览器中完成登录');
      console.log('========================================\n');
      console.log('提示：');
      console.log('  - 扫码、输入密码或使用其他方式登录');
      console.log('  - 完成验证码（如果有）');
      console.log('  - 登录成功后脚本会自动保存\n');
      console.log('最长等待时间：5 分钟\n');

      // 循环检测登录状态
      let loginSuccess = false;
      let attempts = 0;
      const maxAttempts = 60; // 5分钟，每5秒检查一次

      while (!loginSuccess && attempts < maxAttempts) {
        await page.waitForTimeout(5000);
        attempts++;

        const newStatus = await checkLoginStatus(page, context);
        console.log(`[检测 ${attempts}/${maxAttempts}] ${newStatus.details.join(' | ')}`);

        if (newStatus.isLoggedIn) {
          loginSuccess = true;
          console.log('\n✅ 检测到登录成功！');
          break;
        }

        if (attempts % 12 === 0) { // 每分钟提示一次
          console.log(`\n[等待中] 已等待 ${Math.floor(attempts * 5 / 60)} 分钟...\n`);
        }
      }

      if (!loginSuccess) {
        console.log('\n⚠️  超时：未能自动检测到登录状态');
        console.log('如果您已登录，尝试强制保存会话...\n');

        // 强制保存
        loginSuccess = true;
      }

      if (loginSuccess) {
        await page.waitForTimeout(2000);

        // 保存会话
        await context.storageState({ path: sessionFile });

        const stats = fs.statSync(sessionFile);
        const fileSize = (stats.size / 1024).toFixed(2);

        console.log('========================================');
        console.log('  ✅ 登录状态已保存！');
        console.log('========================================\n');
        console.log(`会话文件: session_${domain}.json`);
        console.log(`文件大小: ${fileSize} KB\n`);
        console.log('下次使用时将自动加载此会话！\n');

        console.log('浏览器将在 10 秒后关闭...');
        await page.waitForTimeout(10000);
      }
    }

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
    console.log('\n程序结束');
  }
}

// 解析命令行参数
const args = process.argv.slice(2);
const targetUrl = args[0];
const sessionNameIndex = args.indexOf('--session-name');
const sessionName = sessionNameIndex !== -1 ? args[sessionNameIndex + 1] : null;

// 运行
universalLogin(targetUrl, sessionName).catch(console.error);
