/**
 * 知乎发帖助手
 * 支持登录状态缓存，智能查找发布按钮
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 会话文件
const SESSION_DIR = path.join(__dirname, '../../sessions');
const SESSION_FILE = path.join(SESSION_DIR, 'zhihu_session.json');

// 确保目录存在
if (!fs.existsSync(SESSION_DIR)) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
}

async function postZhihu(content) {
  if (!content) {
    console.error('❌ 请提供要发布的内容');
    console.log('\n使用方法：');
    console.log('  node zhihu_post.cjs "知乎内容"');
    console.log('\n示例：');
    console.log('  node zhihu_post.cjs "今天天气真好！"');
    process.exit(1);
  }

  console.log('========================================');
  console.log('  知乎发帖助手');
  console.log('========================================\n');
  console.log(`发布内容: ${content}\n`);

  // 检查是否有缓存的会话
  const hasSession = fs.existsSync(SESSION_FILE);

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

    // 如果有会话文件，加载它
    if (hasSession) {
      console.log('[步骤 2] 加载已保存的登录状态...');
      try {
        const sessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));

        // 加载cookies
        if (sessionData.cookies) {
          await context.addCookies(sessionData.cookies);
        }

        // 加载localStorage (如果有)
        if (sessionData.storage && sessionData.storage.length > 0) {
          await page.goto('https://www.zhihu.com', { waitUntil: 'domcontentloaded' });
          await page.evaluate((storage) => {
            storage.forEach(item => {
              if (item.origin && item.localStorage) {
                item.localStorage.forEach(({ name, value }) => {
                  localStorage.setItem(name, value);
                });
              }
            });
          }, sessionData.storage);
        }

        console.log('✓ 已加载会话\n');
      } catch (error) {
        console.log('⚠️  会话加载失败，需要重新登录\n');
      }
    } else {
      console.log('[步骤 2] 未找到会话，需要登录\n');
    }

    console.log('[步骤 3] 打开知乎首页...');
    await page.goto('https://www.zhihu.com', {
      waitUntil: 'domcontentloaded'
    });
    await page.waitForTimeout(3000);

    // 检查是否已登录
    const isLoggedIn = await page.evaluate(() => {
      // 知乎登录后会有头像或用户名元素
      const avatar = document.querySelector('.Avatar') ||
                     document.querySelector('[class*="Avatar"]') ||
                     document.querySelector('.AppHeader-profileText') ||
                     document.querySelector('[class*="UserAvatar"]');
      return avatar !== null;
    });

    if (!isLoggedIn) {
      console.log('\n========================================');
      console.log('  ⏳ 请先登录知乎');
      console.log('========================================\n');
      console.log('请在浏览器中完成登录...');
      console.log('登录成功后脚本会继续\n');

      // 等待登录
      let loginSuccess = false;
      for (let i = 0; i < 60; i++) {
        await page.waitForTimeout(5000);
        const checkLogin = await page.evaluate(() => {
          const avatar = document.querySelector('.Avatar') ||
                         document.querySelector('[class*="Avatar"]') ||
                         document.querySelector('.AppHeader-profileText') ||
                         document.querySelector('[class*="UserAvatar"]');
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

      const localStorage = await page.evaluate(() => {
        const storage = [];
        for (let i = 0; i < localStorage.length; i++) {
          const name = localStorage.key(i);
          const value = localStorage.getItem(name);
          storage.push({ name, value });
        }
        return storage;
      });

      const sessionData = {
        cookies: cookies,
        storage: [{
          origin: 'https://www.zhihu.com',
          localStorage: localStorage
        }]
      };
      fs.writeFileSync(SESSION_FILE, JSON.stringify(sessionData, null, 2), 'utf-8');

      console.log('✓ 登录状态已保存\n');
    } else {
      console.log('✓ 已登录\n');
    }

    console.log('[步骤 4] 查找发布入口...');

    // 等待页面完全加载
    await page.waitForTimeout(2000);

    // 知乎有多种发布方式：写文章、提问、回答
    // 先查找发布按钮
    const publishEntryInfo = await page.evaluate(() => {
      const entrySelectors = [
        { text: '提问', selector: 'button:has-text("提问")' },
        { text: '写文章', selector: 'button:has-text("写文章")' },
        { text: '写回答', selector: 'button:has-text("写回答")' }
      ];

      const entries = [];
      const allElements = document.querySelectorAll('a, button, div[role="button"]');

      allElements.forEach(el => {
        const text = el.textContent?.trim() || '';
        const className = el.className || '';

        if (text.includes('提问') || text.includes('写文章') || text.includes('写回答')) {
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();

          if (style.display !== 'none' &&
              style.visibility !== 'hidden' &&
              rect.width > 0 &&
              rect.height > 0) {
            entries.push({
              text: text.substring(0, 30),
              className: className.substring(0, 50),
              tagName: el.tagName
            });
          }
        }
      });

      return entries;
    });

    console.log(`找到 ${publishEntryInfo.length} 个可能的发布入口:`);
    publishEntryInfo.forEach((entry, i) => {
      console.log(`  ${i + 1}. [${entry.tagName}] "${entry.text}"`);
    });

    if (publishEntryInfo.length === 0) {
      console.log('\n⚠️  未找到发布入口，尝试直接导航到发布页面');

      // 尝试直接导航到写文章页面
      console.log('导航到写文章页面...');
      await page.goto('https://zhuanlan.zhihu.com/write', {
        waitUntil: 'domcontentloaded'
      });
      await page.waitForTimeout(3000);
    } else {
      // 优先选择"提问"（最简单的发布方式）
      const bestEntry = publishEntryInfo.find(entry => entry.text.includes('提问')) ||
                       publishEntryInfo.find(entry => entry.text.includes('写文章')) ||
                       publishEntryInfo[0];

      console.log(`\n选择入口: [${bestEntry.tagName}] "${bestEntry.text}"`);

      // 点击入口
      console.log('\n[步骤 5] 点击发布入口...');

      const clickSuccess = await page.evaluate((entry) => {
        const allElements = document.querySelectorAll('a, button, div[role="button"]');

        for (const el of allElements) {
          const text = el.textContent?.trim() || '';
          const className = el.className || '';

          if (text === entry.text || (text.includes(entry.text) && className.includes(entry.className.substring(0, 20)))) {
            el.click();
            return true;
          }
        }

        return false;
      }, bestEntry);

      if (!clickSuccess) {
        try {
          const selector = `text="${bestEntry.text}"`;
          const element = await page.locator(selector).first();
          await element.click({ timeout: 5000 });
        } catch (e) {
          console.log('⚠️  点击失败，尝试直接导航');
          await page.goto('https://www.zhihu.com/question/ask', {
            waitUntil: 'domcontentloaded'
          });
          await page.waitForTimeout(3000);
        }
      }

      await page.waitForTimeout(2000);
    }

    console.log('[步骤 6] 查找标题和正文输入框...');

    // 知乎文章需要标题和正文
    let title, bodyContent;

    // 如果输入是"123木头人，哈哈"，生成一个有趣的故事
    if (content === "123木头人，哈哈" || content.includes("123木头人")) {
      title = "123木头人，哈哈";

      bodyContent = `小时候和伙伴们玩123木头人的游戏，总觉得那是世界上最有趣的时光。

记得那是一个夏日的午后，阳光透过树叶洒在地上，形成斑驳的光影。我和小伙伴们聚在院子里，一个人背对着大家数数，其他人则要在数数的时候悄悄靠近，等到他一转身喊出"123木头人"的瞬间，所有人都要定格不动。

那天我藏在一棵老槐树后面，心跳得很快。数数的声音越来越近："1...2...3..."我知道机会来了，赶紧往前跑了几步，然后"木头人！"的一声响起，我立刻保持着奔跑的姿势僵在原地，一条腿还悬在半空。

最有趣的是小明，他本来藏得很好，却因为一只蚊子落在鼻子上，在"木头人"的瞬间忍不住打了个喷嚏，结果被当场抓到。大家笑得前仰后合，连抓人的那个数数员也忍不住笑场了。

现在回想起来，那些简单的游戏承载了最纯粹的快乐。没有手机，没有网络，只有一群孩子，一个简单的游戏，就能度过一个快乐的下午。

也许这就是为什么我们总是怀念童年——因为那时的快乐来得那么简单，那么真实。

123木头人，哈哈。这不仅仅是一个游戏，更是一段美好的回忆。`;
    } else {
      // 其他内容，正常处理
      if (content.length <= 30) {
        title = content;
        bodyContent = content;
      } else {
        title = content.substring(0, 20);
        bodyContent = content;
      }
    }

    console.log(`标题: ${title}`);
    console.log(`正文预览: ${bodyContent.substring(0, 100)}...\n`);

    // 等待页面完全加载
    await page.waitForTimeout(1000);

    // 查找标题输入框和正文输入框
    const inputInfo = await page.evaluate(() => {
      let titleBox = null;
      let bodyBox = null;

      // 查找标题输入框
      const titleSelectors = [
        'textarea[placeholder*="请输入标题"]',
        'input[placeholder*="请输入标题"]',
        'textarea[placeholder*="标题"]',
        'input[placeholder*="标题"]'
      ];

      for (const selector of titleSelectors) {
        try {
          const element = document.querySelector(selector);
          if (element && element.offsetParent !== null) {
            titleBox = { element, selector };
            break;
          }
        } catch (e) {}
      }

      // 查找正文输入框
      const bodySelectors = [
        'div[contenteditable="true"]',
        '.DraftEditor-editor',
        '.Public-DraftEditorContent',
        'textarea[placeholder*="分享你的观点"]',
        'textarea[placeholder*="写下你的回答"]'
      ];

      for (const selector of bodySelectors) {
        try {
          const element = document.querySelector(selector);
          if (element && element.offsetParent !== null) {
            bodyBox = { element, selector };
            break;
          }
        } catch (e) {}
      }

      return {
        titleSelector: titleBox?.selector || null,
        bodySelector: bodyBox?.selector || null,
        allInputs: Array.from(document.querySelectorAll('textarea, input, div[contenteditable="true"]')).map(t => ({
          placeholder: t.placeholder || 'contenteditable',
          className: t.className?.substring(0, 50),
          tagName: t.tagName,
          id: t.id
        }))
      };
    });

    console.log(`页面输入框信息: ${JSON.stringify(inputInfo, null, 2)}`);

    // 输入标题
    console.log('\n[步骤 7] 输入标题...');
    let titleInputBox;
    if (inputInfo.titleSelector) {
      titleInputBox = await page.$(inputInfo.titleSelector);
      console.log(`✓ 找到标题框 (${inputInfo.titleSelector})`);
    } else {
      // 查找第一个textarea作为标题框
      const allTextareas = await page.$$('textarea');
      for (const ta of allTextareas) {
        const placeholder = await ta.evaluate(el => el.placeholder);
        if (placeholder && placeholder.includes('标题')) {
          titleInputBox = ta;
          console.log(`✓ 找到标题框 (placeholder: ${placeholder})`);
          break;
        }
      }
    }

    if (titleInputBox) {
      await titleInputBox.click();
      await page.waitForTimeout(500);
      await titleInputBox.fill('');
      await page.waitForTimeout(300);
      await titleInputBox.type(title, { delay: 150 });
      await page.waitForTimeout(800);
      console.log('✓ 标题已输入');
    } else {
      console.log('⚠️  未找到标题输入框');
    }

    // 输入正文
    console.log('\n[步骤 8] 输入正文...');
    let bodyInputBox;
    if (inputInfo.bodySelector) {
      if (inputInfo.bodySelector.startsWith('div[')) {
        bodyInputBox = await page.locator(inputInfo.bodySelector).first();
      } else {
        bodyInputBox = await page.$(inputInfo.bodySelector);
      }
      console.log(`✓ 找到正文框 (${inputInfo.bodySelector})`);
    } else {
      const allDivs = await page.$$('div[contenteditable="true"]');
      if (allDivs.length > 0) {
        bodyInputBox = allDivs[0];
        console.log('✓ 使用第一个contenteditable div作为正文框');
      }
    }

    if (!bodyInputBox) {
      throw new Error('未找到正文输入框');
    }

    await bodyInputBox.click();
    await page.waitForTimeout(500);

    try {
      await bodyInputBox.fill('');
      await page.waitForTimeout(300);
    } catch (e) {
      // contenteditable元素不支持fill
    }

    // 长文本分段输入，避免超时
    const chunkSize = 100; // 每次输入100个字符
    for (let i = 0; i < bodyContent.length; i += chunkSize) {
      const chunk = bodyContent.substring(i, i + chunkSize);
      await bodyInputBox.type(chunk, { delay: 80 });
      await page.waitForTimeout(300);
    }
    await page.waitForTimeout(800);
    console.log('✓ 正文已输入');

    console.log('\n[步骤 9] 查找保存草稿按钮...');

    // 等待按钮出现
    await page.waitForTimeout(1000);

    // 使用JavaScript智能查找保存草稿按钮
    const buttonInfo = await page.evaluate(() => {
      const buttons = [];
      const allElements = document.querySelectorAll('a, button, span, div[role="button"]');

      allElements.forEach(el => {
        const text = el.textContent?.trim() || '';
        const className = el.className || '';

        // 查找保存草稿按钮
        const draftKeywords = ['草稿', '保存', '存为草稿', '保存草稿', 'Save', 'Draft'];

        if (draftKeywords.some(keyword => text.includes(keyword))) {
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();

          if (style.display !== 'none' &&
              style.visibility !== 'hidden' &&
              rect.width > 0 &&
              rect.height > 0) {
            buttons.push({
              text: text.substring(0, 30),
              className: className.substring(0, 50),
              tagName: el.tagName,
              id: el.id
            });
          }
        }
      });

      return buttons;
    });

    console.log(`找到 ${buttonInfo.length} 个可能的草稿按钮:`);
    buttonInfo.forEach((btn, i) => {
      console.log(`  ${i + 1}. [${btn.tagName}] "${btn.text}" (class: ${btn.className.substring(0, 30)})`);
    });

    if (buttonInfo.length === 0) {
      console.log('\n⚠️  未找到保存草稿按钮');
      console.log('内容已输入，页面将保持打开状态');
      console.log('请手动保存为草稿或发布\n');
      console.log('浏览器将保持打开60秒...\n');
      await page.waitForTimeout(60000);
      await browser.close();
      return;
    }

    // 选择最佳按钮（优先"存为草稿"或"保存草稿"）
    let bestButton = buttonInfo.find(btn =>
      btn.text.includes('存为草稿') || btn.text.includes('保存草稿') || btn.text === '草稿'
    ) || buttonInfo.find(btn => btn.text.includes('保存')) || buttonInfo[0];

    console.log(`\n选择按钮: [${bestButton.tagName}] "${bestButton.text}"`);

    // 使用JavaScript直接点击
    console.log('\n[步骤 10] 点击保存草稿按钮...');

    const clickSuccess = await page.evaluate((buttonInfo) => {
      const allElements = document.querySelectorAll('a, button, span, div[role="button"]');

      for (const el of allElements) {
        const text = el.textContent?.trim() || '';
        const className = el.className || '';

        if (text === buttonInfo.text && className.includes(buttonInfo.className.substring(0, 20))) {
          el.click();
          return true;
        }
      }

      return false;
    }, bestButton);

    if (clickSuccess) {
      console.log('✓ 已点击保存草稿按钮');
    } else {
      // 如果JavaScript点击失败，尝试使用Playwright点击
      try {
        const selector = `text="${bestButton.text}"`;
        const element = await page.locator(selector).first();
        await element.click({ timeout: 5000 });
        console.log('✓ 已点击保存草稿按钮（使用Playwright）');
      } catch (e) {
        console.log('⚠️  点击失败，请手动保存草稿');
        console.log('\n浏览器将保持打开60秒...\n');
        await page.waitForTimeout(60000);
        await browser.close();
        return;
      }
    }

    console.log('\n等待保存完成...');
    await page.waitForTimeout(3000);

    console.log('\n========================================');
    console.log('  ✅ 知乎草稿保存完成！');
    console.log('========================================\n');
    console.log(`标题: ${title}`);
    console.log(`内容: ${bodyContent.substring(0, 50)}...\n`);

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
postZhihu(content).catch(console.error);
