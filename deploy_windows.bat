@echo off
REM ============================================================
REM  Eve Freelancer Tool — 一键公网部署 (Windows)
REM  在Windows命令行中以管理员身份运行即可
REM ============================================================
TITLE Eve 自由职业者工具 — 公网部署

echo [1/3] 检查 cloudflared...
where cloudflared >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   → 未安装，正在下载...
    curl -sL -o %TEMP%\cloudflared.msi https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi
    msiexec /i %TEMP%\cloudflared.msi /quiet
    echo   ✅ cloudflared 安装完成
) else (
    echo   ✅ cloudflared 已安装
)

echo [2/3] 启动公网隧道...
echo   → 将 localhost:9000 暴露到公网...
echo   → 按 Ctrl+C 停止隧道
echo.

cloudflared tunnel --url http://localhost:9000

echo.
echo [3/3] 隧道已关闭
pause
