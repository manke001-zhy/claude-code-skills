# 敏感信息管理最佳实践

## 核心原则

**永远不要将敏感信息硬编码到代码中或提交到版本控制系统。**

## 敏感信息类型

### 1. 认证凭证
- 用户名/密码
- API Keys
- Access Tokens
- Session IDs
- Cookies

### 2. 配置数据
- 数据库连接字符串
- 第三方服务密钥
- OAuth 凭证
- 私钥/证书

### 3. 用户数据
- 个人信息
- 隐私设置
- 敏感配置

## 推荐方案：.env 文件模式

### 方案一：简单项目 - .env 文件

适用场景：小型脚本、个人项目

#### 目录结构
```
my-skill/
├── .env.example          # 模板文件（可提交）
├── .env.local            # 实际配置（不可提交）
├── .gitignore            # 包含 .env.local
├── config.js             # 读取配置
└── script.js             # 使用配置
```

#### .env.example（可提交）
```bash
# 微博登录配置
WEIBO_USERNAME=your_username
WEIBO_PASSWORD=your_password

# 或使用 cookies
WEIBO_COOKIES_FILE=path/to/cookies.json
```

#### .env.local（不可提交）
```bash
# 实际的敏感信息
WEIBO_USERNAME=zhy
WEIBO_PASSWORD=my_secret_password
```

#### .gitignore
```
# 环境变量文件
.env.local
.env.*.local
.env

# 保留 .env.example
!.env.example
```

#### 使用方式（Node.js）
```javascript
// config.js
import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config({ path: '.env.local' });

export const config = {
  weibo: {
    username: process.env.WEIBO_USERNAME,
    password: process.env.WEIBO_PASSWORD,
  }
};

// script.js
import { config } from './config.js';

console.log(`登录用户: ${config.weibo.username}`);
```

### 方案二：中大型项目 - 配置分离

适用场景：复杂技能、多环境配置

#### 目录结构
```
my-skill/
├── config/
│   ├── default.json      # 默认配置（可提交）
│   ├── development.json  # 开发环境（不可提交）
│   └── production.json   # 生产环境（不可提交）
├── .gitignore
├── load-config.js
└── script.js
```

#### config/default.json（可提交）
```json
{
  "weibo": {
    "baseUrl": "https://weibo.com",
    "timeout": 30000,
    "credentials": {
      "username": "",
      "password": ""
    }
  }
}
```

#### config/development.json（不可提交）
```json
{
  "weibo": {
    "credentials": {
      "username": "zhy",
      "password": "dev_password"
    }
  }
}
```

#### .gitignore
```
config/development.json
config/production.json
config/*.local.json
```

#### 使用方式
```javascript
// load-config.js
import fs from 'fs';
import path from 'path';

function loadConfig(env = 'development') {
  const defaultConfig = JSON.parse(
    fs.readFileSync(path.join('config', 'default.json'))
  );

  const envConfigPath = path.join('config', `${env}.json`);
  let envConfig = {};

  if (fs.existsSync(envConfigPath)) {
    envConfig = JSON.parse(fs.readFileSync(envConfigPath));
  }

  return { ...defaultConfig, ...envConfig };
}

export const config = loadConfig(process.env.NODE_ENV || 'development');
```

### 方案三：Cookies 缓存模式（当前使用）

适用场景：浏览器自动化、需要保持登录状态

#### 目录结构
```
my-skill/
├── .cache/
│   ├── weibo-cookies.json      # 登录 cookies
│   └── weibo-storage.json      # localStorage
├── .gitignore
└── script.js
```

#### .gitignore
```
# 敏感缓存
.cache/
*.cookies.json
*-storage.json
```

#### 安全增强
```javascript
// 可选：加密存储
import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY; // 从 .env 获取
const ALGORITHM = 'aes-256-gcm';

function encrypt(data) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, Buffer.from(ENCRYPTION_KEY), iv);

  let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
}

function decrypt(encryptedData) {
  const decipher = crypto.createDecipheriv(
    ALGORITHM,
    Buffer.from(ENCRYPTION_KEY),
    Buffer.from(encryptedData.iv, 'hex')
  );

  decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

  let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return JSON.parse(decrypted);
}
```

## Git 安全检查清单

### 提交前检查

创建 `scripts/pre-commit-check.sh`：

```bash
#!/bin/bash

echo "🔍 检查敏感信息..."

# 检查暂存文件
STAGED_FILES=$(git diff --cached --name-only)

# 敏感关键词
SENSITIVE_PATTERNS=(
    "password"
    "secret"
    "token"
    "api_key"
    "apikey"
    "access_token"
    "cookie"
    "session"
    "credential"
    "private_key"
)

# 敏感文件扩展名
SENSITIVE_EXTENSIONS=(
    ".env"
    ".pem"
    ".key"
    ".cookies.json"
    "-storage.json"
)

FOUND_ISSUES=0

for file in $STAGED_FILES; do
    # 检查文件扩展名
    for ext in "${SENSITIVE_EXTENSIONS[@]}"; do
        if [[ $file == *$ext ]]; then
            echo "⚠️  发现敏感文件: $file"
            FOUND_ISSUES=1
        fi
    done

    # 检查文件内容
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        if git diff --cached "$file" | grep -i "$pattern" > /dev/null; then
            echo "⚠️  $file 可能包含敏感信息: $pattern"
            FOUND_ISSUES=1
        fi
    done
done

if [ $FOUND_ISSUES -eq 1 ]; then
    echo ""
    echo "❌ 检测到潜在敏感信息！"
    echo "请检查以上文件，确认安全后再提交。"
    echo ""
    echo "如需移除暂存文件："
    echo "  git reset HEAD <file>"
    exit 1
fi

echo "✅ 安全检查通过"
```

### Git Hook 自动检查

```bash
# 安装 pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
bash scripts/pre-commit-check.sh
EOF

chmod +x .git/hooks/pre-commit
```

## 实施步骤

### 步骤 1: 创建 .env.example

```bash
# 为每个技能创建模板
cat > .env.example << 'EOF'
# 敏感信息配置示例
# 复制此文件为 .env.local 并填入实际值

# API 配置
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# 数据库
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password

# 第三方服务
SERVICE_TOKEN=your_service_token
EOF
```

### 步骤 2: 更新 .gitignore

```bash
cat >> .gitignore << 'EOF'

# 环境变量（保留 example）
.env
.env.local
.env.*.local
!.env.example
EOF
```

### 步骤 3: 创建安全检查脚本

将上面的 `pre-commit-check.sh` 保存到 `scripts/` 目录。

### 步骤 4: 团队协作

**README.md 说明：**
```markdown
## 配置

1. 复制环境变量模板：
   ```bash
   cp .env.example .env.local
   ```

2. 在 `.env.local` 中填入你的实际配置

3. ⚠️ **不要提交** `.env.local` 文件

## 安全

- 所有敏感信息都通过环境变量管理
- 提交前会自动检查敏感信息
- 查看 [security-best-practices.md](references/security-best-practices.md)
```

## 工具推荐

### dotenv-safe
```bash
npm install dotenv-safe
```

强制要求所有环境变量都在 `.env.example` 中定义：

```javascript
import dotenvSafe from 'dotenv-safe';

dotenvSafe.config({
  example: '.env.example',
  allowEmptyValues: true
});
```

### dotenv-cli
```bash
npm install -g dotenv-cli

# 运行时注入环境变量
dotenv -e .env.local -- your-script.js
```

## 常见错误

### ❌ 错误做法

```javascript
// 硬编码敏感信息
const API_KEY = "sk-1234567890";

// 提交到仓库
git add .env
git commit -m "Add config"
```

### ✅ 正确做法

```javascript
// 使用环境变量
const API_KEY = process.env.API_KEY;

// .env.example 定义结构
// .env.local 存储实际值（不提交）
```

## 总结

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| .env 文件 | 小型项目 | 简单、通用 | 需要手动管理 |
| 配置分离 | 中大型项目 | 结构清晰、支持多环境 | 配置文件较多 |
| Cookies 缓存 | 浏览器自动化 | 自动管理登录状态 | 需要定期清理 |
| 混合方案 | 复杂项目 | 灵活性高 | 复杂度较高 |

选择适合你项目规模的方案，并坚持执行安全最佳实践。
