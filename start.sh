#!/usr/bin/env bash
# Linux / macOS 一键启动脚本（开发用）
set -e
cd "$(dirname "$0")"

cd backend
if [ ! -d ".venv" ]; then
  echo "→ 创建虚拟环境..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt -q
fi

if [ ! -f "../frontend/dist/index.html" ]; then
  echo "→ 构建前端..."
  cd ../frontend
  [ -d node_modules ] || (pnpm install --no-frozen-lockfile)
  pnpm build:force
  cd ../backend
fi

echo "→ 服务启动：http://127.0.0.1:8000"
( sleep 2 && (xdg-open http://127.0.0.1:8000 2>/dev/null || open http://127.0.0.1:8000 2>/dev/null) ) &

.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
