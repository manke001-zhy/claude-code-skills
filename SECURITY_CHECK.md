# 🔒 安全检查指南

## 自动安全检查已启用

每次 `git commit` 前会自动检查：
- ✅ 敏感文件名（password, secret, token, cookie 等）
- ✅ 本地配置文件（*.local.json, *.env）
- ✅ 会话文件（sessions/, cookies.txt）

## 手动运行安全检查

### 在提交前手动检查

```bash
# 方案1：运行检查脚本
bash scripts/git-security-check.sh

# 方案2：查看即将提交的文件
git status
git diff --cached --name-only

# 方案3：检查是否有敏感文件
git ls-files | grep -E "(secret|token|password|cookie|session|local\.json|\.env)"
```

### 如果误添加了敏感文件

```bash
# 1. 从暂存区移除
git reset HEAD <敏感文件>

# 2. 如果已经提交，从历史中删除
git rm --cached <敏感文件>
git commit --amend

# 3. 更新 .gitignore
echo "<敏感文件>" >> .gitignore
```

## 安全最佳实践

1. **提交前检查**
   - 使用 `git status` 查看要提交的文件
   - 确认没有敏感文件被添加

2. **使用 .local.json 存储配置**
   - 模板文件：`config.json`
   - 本地配置：`config.local.json`（已在 .gitignore 中）

3. **定期审计**
   ```bash
   # 检查所有已跟踪的文件
   git ls-files | grep -iE "(secret|password|token)"

   # 查看最近提交的文件
   git log --name-only --oneline -5
   ```

4. **使用 Git 的忽略功能**
   - 敏感文件添加到 .gitignore
   - 从历史中移除：`git rm --cached <文件>`

## 当前安全状态

✅ 已保护的文件类型：
- `*.local.json` - 本地配置
- `*.env` - 环境变量
- `cookies.txt` - Cookie 文件
- `sessions/` - 会话目录
- `.cache/` - 缓存目录
- `*secret*`, `*token*`, `*password*` - 敏感关键词

✅ 最近的安全修复：
- 已从版本控制中移除 `bilibili-subtitle-extractor/cookies.txt`
- 更新 .gitignore 防止再次提交

## 紧急处理

如果发现敏感信息已泄露到 GitHub：

1. **立即更改密码/令牌**
2. **从 git 历史中删除**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch <敏感文件>" \
     --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
3. **撤销所有已登录设备**
4. **重新生成访问令牌**
