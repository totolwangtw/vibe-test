@echo off
chcp 65001 > nul
title 项目管理工具 - 本地服务

REM =================================================================
REM 项目管理工具 - Windows 一键启动脚本
REM 说明：
REM   1. 需要 Windows 上已安装 Python 3.10+（推荐 3.12）
REM      下载地址：https://www.python.org/downloads/
REM      安装时请勾选 "Add Python to PATH"
REM   2. 双击本文件即可启动，浏览器会自动打开 http://127.0.0.1:8000
REM   3. 首次启动会自动创建虚拟环境、安装依赖、初始化数据库
REM   4. 关闭窗口或按 Ctrl+C 即可停止服务
REM =================================================================

cd /d "%~dp0"

echo ========================================
echo   项目管理工具 - 启动中...
echo ========================================
echo.

REM 检测 Python
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
  ) else (
    set "PY=py"
  )
) else (
  set "PY=python"
)

REM 创建虚拟环境（首次）
if not exist "backend\.venv" (
  echo [初始化] 创建虚拟环境...
  %PY% -m venv backend\.venv
  if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
  )
)

REM 激活虚拟环境
call "backend\.venv\Scripts\activate.bat"

REM 安装依赖（首次或更新时）
if not exist "backend\.venv\.installed" (
  echo [初始化] 安装后端依赖（首次启动需要 1-2 分钟）...
  python -m pip install --upgrade pip -q
  python -m pip install -r backend\requirements.txt -q
  if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络
    pause
    exit /b 1
  )
  echo done > "backend\.venv\.installed"
)

REM 检查前端是否已构建
if not exist "frontend\dist\index.html" (
  echo [警告] 未检测到前端构建产物 frontend\dist\
  echo        请先在开发环境执行：cd frontend ^&^& pnpm install ^&^& pnpm build
  echo        或将已构建的 dist 目录拷贝到 frontend\ 下
  pause
  exit /b 1
)

echo.
echo ========================================
echo   服务已启动！
echo   地址：http://127.0.0.1:8000
echo   API 文档：http://127.0.0.1:8000/docs
echo   关闭窗口或按 Ctrl+C 即可停止
echo ========================================
echo.

REM 延迟 2 秒后自动打开浏览器
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000"

REM 启动 FastAPI 服务
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info

pause
