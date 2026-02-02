#!/bin/bash
# Git 安全检查脚本
# 在 commit 前自动检查敏感信息

echo "🔒 安全检查中..."

# 敏感关键词列表
SENSITIVE_KEYWORDS=(
    "password.*=.*[^your_]"
    "api_key.*=.*[^your_]"
    "secret.*=.*[^your_]"
    "token.*=.*[^your_]"
    "auth.*=.*[^your_]"
    "cookie"
    "session"
    "credential"
)

# 敏感文件扩展名
SENSITIVE_PATTERNS=(
    "*.local.json"
    "*.env"
    "*secret*"
    "*token*"
    "*password*"
    "cookies.txt"
    "cookies*.json"
    "*.session.json"
    "sessions/"
)

# 检查暂存区文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "✓ 没有文件要提交"
    exit 0
fi

echo "📝 准备提交的文件："
echo "$STAGED_FILES" | while read file; do
    echo "  - $file"
done

# 检查敏感文件
HAS_ISSUE=0

echo ""
echo "🔍 检查敏感文件..."

for file in $STAGED_FILES; do
    # 检查文件名是否匹配敏感模式
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            echo "⚠️  警告：敏感文件 $file 被添加到暂存区！"
            HAS_ISSUE=1
        fi
    done

    # 检查文件内容（只检查文本文件）
    if [[ "$file" == *.json || "$file" == *.py || "$file" == *.js || "$file" == *.cjs || "$file" == *.yaml || "$file" == *.yml || "$file" == *.md ]]; then
        for keyword in "${SENSITIVE_KEYWORDS[@]}"; do
            if git show :"$file" 2>/dev/null | grep -iE "$keyword" | grep -v "your_" | grep -v "placeholder" | grep -v "example" > /dev/null; then
                echo "⚠️  警告：$file 可能包含敏感信息（匹配: $keyword）"
                echo "   请检查文件内容"
                HAS_ISSUE=1
            fi
        done
    fi
done

if [ $HAS_ISSUE -eq 1 ]; then
    echo ""
    echo "❌ 发现安全问题！请："
    echo "   1. 检查上述文件"
    echo "   2. 移除敏感信息"
    echo "   3. 更新 .gitignore"
    echo ""
    echo "如需强制提交，使用: git commit --no-verify"
    exit 1
fi

echo "✓ 安全检查通过"
exit 0
