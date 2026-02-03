# Dev Browser 技能 - 文件结构说明

## 📁 目录结构

```
dev-browser/
├── client.js                    # 客户端连接核心
├── server.js                    # 服务器（独立模式）
├── server-extension.js          # 扩展模式服务器
├── package.json                 # 项目配置
├── tsconfig.json                # TypeScript配置
├── SKILL.md                     # 技能使用文档
├── INSTALL.md                   # 安装指南
├── README.md                    # 本文件
│
├── scripts/                     # 脚本目录
│   ├── universal/               # 通用脚本（所有网站）
│   │   └── universal_login.js   # 通用网站登录助手
│   │
│   └── site-specific/           # 网站特定脚本
│       └── baidu_search.js      # 百度搜索助手
│
└── sessions/                    # 登录会话存储
    ├── bilibili_session.json    # 哔哩哔哩会话
    ├── zhihu_session.json       # 知乎会话
    └── session_www_baidu_com.json  # 百度会话
```

## 🚀 快速开始

### 1. 通用网站登录（万能工具）

适用于任意网站的登录和会话保存：

```bash
# 基本用法
cd ~/.claude/skills/dev-browser
node scripts/universal/universal_login.js https://网站URL

# 示例
node scripts/universal/universal_login.js https://www.zhihu.com
node scripts/universal/universal_login.js https://github.com

# 自定义会话名称
node scripts/universal/universal_login.js https://网站URL --session-name 自定义名称
```

**功能特点：**
- ✅ 智能检测登录状态（4种方法交叉验证）
- 💾 自动保存会话（cookies + storage）
- 🔄 自动复用已保存会话（7天内）
- ⏰ 超时自动保存（5分钟等待）
- 🌐 通用所有网站

### 2. 百度搜索助手

使用已登录的百度账号搜索并打开结果：

```bash
cd ~/.claude/skills/dev-browser
node scripts/site-specific/baidu_search.js 搜索关键词

# 示例
node scripts/site-specific/baidu_search.js 微博
node scripts/site-specific/baidu_search.js Claude AI
```

**前提条件：**
- 需要先使用 `universal_login.js` 登录百度并保存会话

### 3. 微博热搜话题抓取

抓取微博热搜榜并保存为JSON文件：

```bash
cd ~/.claude/skills/dev-browser
node scripts/site-specific/weibo_topics.cjs
```

**输出位置：**
- 桌面/微博热搜榜/hot_topics.json
- 桌面/微博热搜榜/screenshots/（每个话题的截图）

**功能：**
- 自动检测登录状态
- 抓取完整热搜榜（50条）
- 保存话题数据为JSON格式
- 为每个话题生成截图

### 4. 微博热搜榜截图

截取微博热搜榜高清图片：

```bash
cd ~/.claude/skills/dev-browser
node scripts/site-specific/weibo_screenshot.cjs
```

**输出位置：**
- 桌面/微博热搜榜/hot_topics_full.png（完整截图）

**功能：**
- 支持登录缓存（首次登录后保存cookies）
- 高分辨率截图（1920x1080, 2x像素密度）
- 首次需要扫码登录，后续自动使用缓存

**缓存位置：**
- `dev-browser/.cache/weibo-cookies.json`
- `dev-browser/.cache/weibo-storage.json`

### 5. 百家号内容管理

百家号平台的登录、发布和内容管理工具：

```bash
# 登录并保存cookies（首次使用）
cd ~/.claude/skills/dev-browser
node scripts/site-specific/baijiahao_login.cjs

# 完整发布流程（登录→编辑→发布）
node scripts/site-specific/baijiahao_full_save.cjs

# 快速保存（使用已缓存的登录状态）
node scripts/site-specific/baijiahao_quick_save.cjs

# 查看已发布内容数据
node scripts/site-specific/baijiahao_view_data.cjs
```

**功能：**
- 支持登录状态缓存（.cache/baijiahao-cookies.json）
- 自动保存百家号登录状态
- 发布内容到百家号平台
- 查看和管理已发布内容

**缓存位置：**
- `dev-browser/.cache/baijiahao-cookies.json`
- `dev-browser/.cache/baijiahao-storage.json`

### 6. B站登录状态检查

检查哔哩哔哩登录是否有效：

```bash
cd ~/.claude/skills/dev-browser
node scripts/site-specific/bilibili_login_check.cjs
```

**功能：**
- 检查已保存的B站会话是否有效
- 返回登录状态和用户信息

## 📝 会话文件说明

### 会话文件位置
所有会话文件保存在 `sessions/` 目录下，文件名格式为 `session_域名.json`

### 会话文件内容
包含：
- **Cookies**: 登录凭证
- **LocalStorage**: 本地存储数据
- **SessionStorage**: 会话存储数据

### 会话有效期
- 自动检测：会话创建后7天内自动使用
- 手动刷新：会话过期后重新运行登录脚本即可

## 🔧 脚本开发指南

### 添加新的网站特定脚本

1. 在 `scripts/site-specific/` 创建新脚本
2. 引用会话文件时使用相对路径：
   ```javascript
   const sessionFile = path.join(__dirname, '../../sessions/会话文件名.json');
   ```
3. 先使用 `universal_login.js` 保存该网站的登录会话
4. 在脚本中加载会话文件即可使用已保存的登录状态

### 示例：创建微博搜索脚本

```javascript
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sessionFile = path.join(__dirname, '../../sessions/session_weibo_com.json');

// 使用已保存的会话
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({
  storageState: sessionFile
});
// ... 继续你的操作
```

## 🛠️ 故障排除

### 问题1：找不到会话文件
**解决方案：** 先运行 `universal_login.js` 登录并保存会话

### 问题2：会话已失效
**解决方案：** 重新运行 `universal_login.js` 刷新会话

### 问题3：脚本找不到模块
**解决方案：** 确保在 `dev-browser/` 目录下运行脚本，或使用绝对路径

## 📚 更多资源

- **技能文档**: 查看 `SKILL.md` 了解完整的API和使用方法
- **安装指南**: 查看 `INSTALL.md` 了解安装和配置
- **Playwright文档**: https://playwright.dev/

## ⚙️ 配置文件

- `package.json`: 项目依赖和脚本配置
- `tsconfig.json`: TypeScript编译配置
- `tsconfig.json` 中的 `@/` 别名指向 `dev-browser/` 目录

## 🎯 最佳实践

1. **使用通用登录脚本**: 优先使用 `universal_login.js` 处理登录
2. **会话管理**: 定期刷新会话（建议每周一次）
3. **脚本组织**: 通用脚本放 `universal/`，网站特定脚本放 `site-specific/`
4. **路径引用**: 始终使用相对路径引用会话文件

---

**更新时间**: 2026-02-03
**维护者**: 编剧小助理 🎬
