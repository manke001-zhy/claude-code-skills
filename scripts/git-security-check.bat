@echo off
REM Git 安全检查脚本 (Windows 版本)
REM 在 commit 前自动检查敏感信息

echo 🔒 安全检查中...

REM 获取暂存区文件
for /f "delims=" %%i in ('git diff --cached --name-only --diff-filter=ACM') do set STAGED_FILES=%%i

if "%STAGED_FILES%"=="" (
    echo ✓ 没有文件要提交
    exit /b 0
)

echo 📝 准备提交的文件：
git diff --cached --name-only --diff-filter=ACM

echo.
echo 🔍 检查敏感文件...

REM 检查敏感文件
git diff --cached --name-only | findstr /i "local.json .env secret token password cookie session credential" >nul
if %errorlevel%==0 (
    echo.
    echo ❌ 发现可能的敏感文件！
    echo 请检查：
    git diff --cached --name-only | findstr /i "local.json .env secret token password cookie session credential"
    echo.
    echo 如需强制提交，使用: git commit --no-verify
    exit /b 1
)

echo ✓ 安全检查通过
exit /b 0
