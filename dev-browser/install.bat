@echo off
echo ========================================
echo   Dev-Browser 依赖安装
echo ========================================
echo.

cd /d C:\Users\manke\.claude\skills\dev-browser

echo [1/2] 正在安装 npm 依赖包...
call npm install --registry=https://registry.npmmirror.com
if %errorlevel% neq 0 (
    echo.
    echo [错误] npm install 失败！
    pause
    exit /b 1
)

echo.
echo [2/2] 正在安装 Playwright 浏览器...
call npx playwright install chromium
if %errorlevel% neq 0 (
    echo.
    echo [错误] Playwright 安装失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
pause
