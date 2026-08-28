#!/usr/bin/env bash
# =============================================================================
# 生成自签名 SSL 证书（本地 / 局域网 HTTPS 测试用）
# =============================================================================
# 用法：
#   cd /workspace/deploy/nginx
#   ./self-signed-cert.sh
#
# 可选环境变量：
#   DOMAIN    访问域名或 IP，默认 localhost；局域网可设为本机 IP，如 192.168.1.10
#   DAYS      证书有效期天数，默认 825
#   OUT_DIR   证书输出目录，默认 ./certs（即 /workspace/deploy/nginx/certs）
#
# 生成后拷贝到 Nginx 配置中指定的路径，例如：
#   sudo mkdir -p /etc/nginx/ssl
#   sudo cp certs/pm-tool.crt certs/pm-tool.key /etc/nginx/ssl/
# =============================================================================
set -e

cd "$(dirname "$0")"

DOMAIN="${DOMAIN:-localhost}"
DAYS="${DAYS:-825}"
OUT_DIR="${OUT_DIR:-./certs}"
mkdir -p "$OUT_DIR"

CRT="$OUT_DIR/pm-tool.crt"
KEY="$OUT_DIR/pm-tool.key"

echo "→ 生成自签名证书（域名/IP：$DOMAIN，有效期 $DAYS 天）..."

# 一步生成私钥 + 自签名证书，含 SAN（IP/域名）以兼容现代浏览器
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$KEY" \
  -out "$CRT" \
  -days "$DAYS" \
  -subj "/C=CN/ST=Local/L=Local/O=PM-Tool/CN=$DOMAIN" \
  -addext "subjectAltName=DNS:localhost,DNS:$DOMAIN,IP:127.0.0.1$(echo \"$DOMAIN\" | grep -Eq '^[0-9.]+$' && echo \",IP:$DOMAIN\" || true)"

# 设置私钥权限
chmod 600 "$KEY"

echo ""
echo "✓ 证书已生成："
echo "   证书：$(pwd)/$CRT"
echo "   私钥：$(pwd)/$KEY"
echo ""
echo "→ 拷贝到 Nginx 配置路径（按需修改）："
echo "   sudo mkdir -p /etc/nginx/ssl"
echo "   sudo cp $CRT $KEY /etc/nginx/ssl/"
echo ""
echo "→ 测试并重载 Nginx："
echo "   sudo nginx -t && sudo nginx -s reload"
echo ""
echo "提示：自签名证书浏览器会提示\"不安全\"，可手动信任。"
echo "      公网域名建议使用 Let's Encrypt："
echo "      sudo certbot --nginx -d your-domain.com"
