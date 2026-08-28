#!/usr/bin/env bash
# =============================================================================
# 生产环境启动脚本 - Nginx 反向代理 + HTTPS 模式
# =============================================================================
# 启动顺序：
#   1) 启动后端（本脚本，监听 127.0.0.1:8000，信任代理头）
#   2) 启动 / 重载 Nginx（加载 deploy/nginx/pm-tool.conf）
#
# 用法：
#   ./start-prod.sh              # 前台运行（看日志）
#   PM_PROXY_HEADERS=true ./start-prod.sh   # 显式开启代理头
#
# 环境变量（可选）：
#   PM_HOST            监听地址，默认 127.0.0.1（仅本机，由 Nginx 转发）
#   PM_PORT            监听端口，默认 8000
#   PM_PROXY_HEADERS   是否信任代理头，默认 true（生产环境）
# =============================================================================
set -e
cd "$(dirname "$0")/../.."   # 切到项目根目录 /workspace

cd backend

# 确保虚拟环境
if [ ! -d ".venv" ]; then
  echo "→ 创建虚拟环境..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt -q
fi

# 确保前端已构建
if [ ! -f "../frontend/dist/index.html" ]; then
  echo "→ 构建前端..."
  cd ../frontend
  [ -d node_modules ] || pnpm install --no-frozen-lockfile
  pnpm build:force
  cd ../backend
fi

# 默认开启代理头（生产部署在 Nginx 后）
export PM_PROXY_HEADERS="${PM_PROXY_HEADERS:-true}"
export PM_HOST="${PM_HOST:-127.0.0.1}"
export PM_PORT="${PM_PORT:-8000}"

echo "============================================"
echo "  生产模式启动（Nginx + HTTPS 反向代理）"
echo "  后端监听：http://${PM_HOST}:${PM_PORT}"
echo "  对外入口：https://<域名或IP>（由 Nginx 提供）"
echo "  代理头信任：${PM_PROXY_HEADERS}"
echo "  按 Ctrl+C 停止"
echo "============================================"

# 后台常驻可用：nohup .venv/bin/python -m uvicorn ... > /var/log/pm-tool.log 2>&1 &
.venv/bin/python -m uvicorn app.main:app \
  --host "${PM_HOST}" --port "${PM_PORT}" \
  --proxy-headers \
  --forwarded-allow-ips "${PM_FORWARDED_ALLOW_IPS:-127.0.0.1}" \
  --log-level info
