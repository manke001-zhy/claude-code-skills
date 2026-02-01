# Dev Browser 技能安装指南

## 当前状态
由于网络连接问题，无法从 GitHub 自动克隆完整的 dev-browser 技能。以下是手动安装的几种方法：

## 方法 1：从 GitHub 手动下载（推荐）

### 步骤：
1. 访问 https://github.com/SawyerHood/dev-browser
2. 点击绿色 "Code" 按钮 → "Download ZIP"
3. 解压到 `C:\Users\manke\.claude\skills\dev-browser`
4. 打开终端，进入目录：
   ```bash
   cd ~/.claude/skills/dev-browser
   ```
5. 安装依赖：
   ```bash
   npm install
   ```
6. 安装 Playwright 浏览器：
   ```bash
   npx playwright install chromium
   ```

## 方法 2：使用代理或 VPN

如果你有可用的代理或 VPN：

1. 启用你的代理/VPN
2. 配置 Git 代理（如果需要）：
   ```bash
   git config --global http.proxy http://127.0.0.1:7890
   ```
3. 克隆仓库：
   ```bash
   cd ~/.claude/skills
   git clone https://github.com/SawyerHood/dev-browser.git
   ```
4. 进入目录并安装依赖：
   ```bash
   cd dev-browser
   npm install
   npx playwright install chromium
   ```

## 方法 3：使用其他下载方式

### 使用国内镜像：
```bash
cd ~/.claude/skills
git clone https://gitee.com/mirrors/dev-browser.git
```

## 安装后的验证

安装完成后，运行以下命令验证：

```bash
cd ~/.claude/skills/dev-browser
npx tsx -e "import { chromium } from 'playwright'; console.log('Playwright installed successfully')"
```

## 启动服务器

### Standalone 模式（默认）：
```bash
cd ~/.claude/skills/dev-browser
./server.sh
```

或使用 headless 模式：
```bash
cd ~/.claude/skills/dev-browser
npx tsx server.js --headless
```

### Extension 模式：
1. 首先安装浏览器扩展：https://github.com/SawyerHood/dev-browser/releases
2. 启动中继服务器：
   ```bash
   cd ~/.claude/skills/dev-browser
   npm run start-extension
   ```
3. 在浏览器中激活扩展

## 常见问题

### Q: npm install 没有反应
A: 尝试：
- 使用 pnpm: `pnpm install`
- 使用 yarn: `yarn install`
- 检查网络连接
- 清除 npm 缓存: `npm cache clean --force`

### Q: Playwright 浏览器下载失败
A: 使用国内镜像：
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
npx playwright install chromium
```

### Q: 找不到 tsx 命令
A: 全局安装 tsx：
```bash
npm install -g tsx
```

## 完成安装的标志

安装成功后，你应该有以下文件结构：
```
~/.claude/skills/dev-browser/
├── SKILL.md
├── package.json
├── tsconfig.json
├── client.js
├── server.js
├── server-extension.js
├── server.sh
├── references/
│   └── scraping.md
└── node_modules/
    ├── playwright/
    ├── tsx/
    └── ...
```

## 需要帮助？

如果以上方法都无法完成安装，请检查：
1. Node.js 版本是否 >= 18
2. 网络连接是否正常
3. 是否有足够的磁盘空间
4. 防火墙/杀毒软件是否阻止了下载

生成时间: 2026-02-02
