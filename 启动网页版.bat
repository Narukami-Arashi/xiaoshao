@echo off
chcp 65001 >nul 2>&1
title 小哨 Web 版
cd /d "%~dp0"

echo ==========================================
echo   校园反诈助手「小哨」Web 版
echo ==========================================
echo.
echo 正在检查依赖...

py -c "import flask" 2>nul
if errorlevel 1 (
    echo 正在安装 Flask...
    py -m pip install flask flask-cors -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo 安装失败,请手动运行: py -m pip install flask flask-cors
        pause
        exit /b 1
    )
)

echo.
echo 正在获取本机局域网地址...
py -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print('  手机(同一WiFi)请访问: http://'+s.getsockname()[0]+':5000'); s.close()" 2>nul
echo   本机请访问: http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 可以停止服务
echo.

py web_app.py

pause