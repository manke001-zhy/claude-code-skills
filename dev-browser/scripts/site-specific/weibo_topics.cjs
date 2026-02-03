/**
 * 微博热门话题抓取脚本 - 自动检测登录版本
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const os = require('os');

// 保存到桌面
const desktopPath = path.join(os.homedir(), 'Desktop');
const OUTPUT_DIR = path.join(desktopPath, '微博热搜榜');
const SCREENSHOT_DIR = path.join(OUTPUT_DIR, 'screenshots');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function main() {
  console.log('🚀 启动浏览器...');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
  });

  // 使用更高的分辨率和设备像素比
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2, // 2倍像素密度，提高清晰度
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  // 监听所有导航事件
  let isLoggedIn = false;

  page.on('load', () => {
    const url = page.url();
    console.log('📍 当前页面:', url);

    // 检测是否已登录成功（URL包含weibo.com且不是登录页）
    if (url.includes('weibo.com') && !url.includes('login.php') && !url.includes('/signup')) {
      isLoggedIn = true;
    }
  });

  console.log('📱 正在打开微博登录页面...');
  try {
    await page.goto('https://weibo.com/newlogin', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });
  } catch (error) {
    console.log('⚠️ 页面加载超时，尝试继续...');
  }

  console.log('');
  console.log('='.repeat(60));
  console.log('⚠️  请在浏览器中扫码登录微博');
  console.log('   脚本会自动检测登录状态并继续...');
  console.log('='.repeat(60));
  console.log('');

  // 轮询检查登录状态，最多等待2分钟
  const maxWaitTime = 120000; // 2分钟
  const checkInterval = 2000; // 每2秒检查一次
  let elapsedTime = 0;

  while (!isLoggedIn && elapsedTime < maxWaitTime) {
    await page.waitForTimeout(checkInterval);
    elapsedTime += checkInterval;

    // 检查URL变化
    const currentUrl = page.url();
    if (currentUrl.includes('weibo.com') &&
        !currentUrl.includes('login') &&
        !currentUrl.includes('signup') &&
        !currentUrl.includes('visitor')) {
      isLoggedIn = true;
      break;
    }

    // 每10秒显示一次等待提示
    if (elapsedTime % 10000 === 0) {
      console.log(`⏳ 等待登录中... (${elapsedTime/1000}秒)`);
    }
  }

  if (!isLoggedIn) {
    console.log('❌ 登录超时，请重试');
    await browser.close();
    return;
  }

  console.log('✅ 检测到登录成功！');
  await page.waitForTimeout(2000);

  // 访问微博热搜榜
  console.log('🔥 正在前往微博热搜榜...');
  await page.goto('https://s.weibo.com/top/summary', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });

  await page.waitForTimeout(3000);

  // 截取整个热搜榜页面 - 高清截图
  console.log('📸 正在截图热搜榜页面...');
  await page.screenshot({
    path: path.join(OUTPUT_DIR, 'hot_topics_full.png'),
    fullPage: true,
    type: 'png'
  });
  console.log('✅ 完整热搜榜已保存:', path.join(OUTPUT_DIR, 'hot_topics_full.png'));

  // 获取前10个热搜话题
  console.log('📊 正在提取前10个热搜话题...');

  const topics = await page.evaluate(() => {
    const items = [];
    const rows = document.querySelectorAll('#pl_top_realtimehot table tbody tr');

    for (let i = 0; i < Math.min(10, rows.length); i++) {
      const row = rows[i];
      const rankCell = row.querySelector('td.td-01');
      const textCell = row.querySelector('td.td-02 a');
      const numCell = row.querySelector('td.td-03');

      if (textCell) {
        items.push({
          rank: rankCell?.textContent?.trim() || (i + 1).toString(),
          title: textCell.textContent?.trim() || '',
          heat: numCell?.textContent?.trim() || '',
          url: textCell.getAttribute('href') || ''
        });
      }
    }

    return items;
  });

  console.log('');
  console.log('='.repeat(60));
  console.log('🔥 微博热搜榜 TOP 10');
  console.log('='.repeat(60));

  // 保存结果到JSON
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'hot_topics.json'),
    JSON.stringify(topics, null, 2),
    'utf-8'
  );

  // 显示话题列表
  topics.forEach((topic, i) => {
    console.log(`\n${topic.rank}. ${topic.title}`);
    console.log(`   🔥 热度: ${topic.heat}`);
  });

  // 逐个截图每个话题
  console.log('\n📸 开始逐个截图...');
  for (let i = 0; i < topics.length; i++) {
    const topic = topics[i];
    console.log(`\n正在处理 ${i + 1}/${topics.length}: ${topic.title}`);

    if (topic.url) {
      const fullUrl = topic.url.startsWith('http') ? topic.url : `https://s.weibo.com${topic.url}`;
      try {
        await page.goto(fullUrl, {
          waitUntil: 'domcontentloaded',
          timeout: 30000
        });
        await page.waitForTimeout(2000);

        const screenshotPath = path.join(SCREENSHOT_DIR, `${String(i + 1).padStart(2, '0')}_${topic.title.replace(/[\\/:*?"<>|]/g, '_')}.png`);
        await page.screenshot({
          path: screenshotPath,
          fullPage: true
        });
        console.log(`   ✅ 截图已保存`);

      } catch (error) {
        console.log(`   ⚠️  无法访问该话题: ${error.message}`);
      }
    }
  }

  console.log('');
  console.log('='.repeat(60));
  console.log('✅ 完成！所有截图已保存到:');
  console.log(`   ${SCREENSHOT_DIR}`);
  console.log(`   ${path.join(OUTPUT_DIR, 'hot_topics.json')}`);
  console.log('='.repeat(60));

  // 显示保存的文件列表
  const files = fs.readdirSync(SCREENSHOT_DIR);
  console.log(`\n📁 共保存 ${files.length} 个截图文件:`);
  files.forEach(file => console.log(`   - ${file}`));

  console.log('');
  console.log('💡 浏览器将保持打开10秒后自动关闭...');

  await page.waitForTimeout(10000);
  await browser.close();
}

main().catch(console.error);
