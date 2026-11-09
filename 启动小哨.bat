@echo off
chcp 65001 >nul 2>&1
title 校园反诈助手 - 小哨
cd /d "%~dp0"

echo 正在启动小哨...
echo.

py xiaoshao/main.py
if errorlevel 1 (
    echo.
    echo 启动失败!请检查:
    echo   1. 是否已安装 Python (python.org 下载安装,勾选 Add to PATH)
    echo   2. .env 文件里的 LLM_API_KEY 是否已填写
    echo.
    pause
)