/**
 * B站登录检查助手
 * 打开B站并检查登录状态，未登录则显示二维码
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const COOKIES_FILE = path.join(__dirname, '../../bilibili-subtitle-extractor/cookies.txt');

async function checkBilibiliLogin() {
  console.log('========================================');
  console.log('  B站登录检查助手');
  console.log('========================================\n');

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

    // 加载已保存的 cookies
    if (fs.existsSync(COOKIES_FILE)) {
      console.log('[步骤 2] 加载已保存的 cookies...');
      try {
        const cookies = parseCookiesFile(COOKIES_FILE);
        if (cookies.length > 0) {
          await context.addCookies(cookies);
          console.log(`✓ 已加载 ${cookies.length} 个 cookies\n`);
        }
      } catch (error) {
        console.log('⚠️  Cookies 加载失败\n');
      }
    } else {
      console.log('[步骤 2] 未找到 cookies 文件\n');
    }

    console.log('[步骤 3] 打开 B站 首页...');
    await page.goto('https://www.bilibili.com', {
      waitUntil: 'domcontentloaded'
    });
    await page.waitForTimeout(3000);

    // 检查是否已登录
    const isLoggedIn = await page.evaluate(() => {
      // 查找登录后的头像或用户信息
      const avatar = document.querySelector('.header-avatar-wrap') ||
                     document.querySelector('.nav-user-info') ||
                     document.querySelector('[class*="avatar"]');
      return avatar !== null;
    });

    if (isLoggedIn) {
      console.log('\n========================================');
      console.log('  ✅ 已登录 B站！');
      console.log('========================================\n');

      // 获取用户信息
      const userInfo = await page.evaluate(() => {
        const avatar = document.querySelector('.header-avatar-wrap');
        const userName = document.querySelector('.nav-user-text') ||
                         document.querySelector('[class*="user-name"]');
        return {
          avatar: avatar ? '已找到头像' : '未找到',
          userName: userName ? userName.textContent.trim() : '未知'
        };
      });

      console.log(`用户信息: ${JSON.stringify(userInfo, null, 2)}\n`);

      // 更新 cookies
      console.log('更新 cookies...');
      const cookies = await context.cookies();
      saveCookiesFile(cookies, COOKIES_FILE);
      console.log('✓ Cookies 已保存\n');

    } else {
      console.log('\n========================================');
      console.log('  ⏳ 未登录，请扫码登录');
      console.log('========================================\n');
      console.log('正在打开登录页面...\n');

      // 点击登录按钮
      try {
        // 查找并点击登录按钮
        const loginButton = await page.locator('text=登录').first();
        await loginButton.click();
        await page.waitForTimeout(2000);

        console.log('✓ 请扫描屏幕上的二维码登录\n');
        console.log('登录成功后，脚本会自动保存 cookies\n');

        // 等待登录
        let loginSuccess = false;
        for (let i = 0; i < 120; i++) {  // 最多等待10分钟
          await page.waitForTimeout(5000);

          const checkLogin = await page.evaluate(() => {
            const avatar = document.querySelector('.header-avatar-wrap') ||
                           document.querySelector('.nav-user-info');
            return avatar !== null;
          });

          if (checkLogin) {
            loginSuccess = true;
            break;
          }

          if (i % 12 === 0) {  // 每分钟提示一次
            console.log(`等待登录中... ${Math.floor(i / 12)} 分钟`);
          }
        }

        if (loginSuccess) {
          console.log('\n✅ 登录成功！');

          // 保存 cookies
          const cookies = await context.cookies();
          saveCookiesFile(cookies, COOKIES_FILE);
          console.log('✓ Cookies 已保存\n');
        } else {
          console.log('\n⚠️  登录超时');
        }

      } catch (error) {
        console.log('⚠️  打开登录页面失败，请手动登录');
      }
    }

    console.log('浏览器将保持打开 30 秒...');
    await page.waitForTimeout(30000);

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n程序结束');
    }
  }
}

// 解析 cookies.txt 文件
function parseCookiesFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const cookies = [];

  for (const line of lines) {
    if (line.startsWith('#') || !line.trim()) continue;

    const parts = line.split('\t');
    if (parts.length >= 7) {
      cookies.push({
        name: parts[5],
        value: parts[6],
        domain: parts[0],
        path: parts[2],
        secure: parts[3] === 'TRUE',
        httpOnly: false, // Netscape 格式不支持 httpOnly 标志
        sameSite: 'Lax',
        expirationDate: parts[4] ? parseInt(parts[4]) : undefined
      });
    }
  }

  return cookies;
}

// 保存 cookies 到文件
function saveCookiesFile(cookies, filePath) {
  let content = '# Netscape HTTP Cookie File\n';
  content += '# This file is generated by browser automation. Do not edit.\n\n';

  for (const cookie of cookies) {
    const secure = cookie.secure ? 'TRUE' : 'FALSE';
    const expires = cookie.expirationDate || Math.floor(Date.now() / 1000) + 3600 * 24 * 30;

    content += `${cookie.domain}\tTRUE\t${cookie.path || '/'}\t${secure}\t${expires}\t${cookie.name}\t${cookie.value}\n`;
  }

  fs.writeFileSync(filePath, content, 'utf-8');
}

// 运行
checkBilibiliLogin().catch(console.error);
