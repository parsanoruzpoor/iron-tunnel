#!/bin/bash
set -e

INSTALL_DIR="/opt/iron-tunnel"

apt update -y
apt install -y python3 python3-pip curl

pip3 install cryptography >/dev/null 2>&1 || true

mkdir -p $INSTALL_DIR/core $INSTALL_DIR/configs

BASE_URL="https://raw.githubusercontent.com/parsanoruzpoor/iron-tunnel/main"

curl -fsSL $BASE_URL/iron.py -o $INSTALL_DIR/iron.py
curl -fsSL $BASE_URL/core/crypto.py -o $INSTALL_DIR/core/crypto.py
curl -fsSL $BASE_URL/core/balance.py -o $INSTALL_DIR/core/balance.py
curl -fsSL $BASE_URL/core/obfs.py -o $INSTALL_DIR/core/obfs.py
curl -fsSL $BASE_URL/core/__init__.py -o $INSTALL_DIR/core/__init__.py
curl -fsSL $BASE_URL/configs/tunnel.json -o $INSTALL_DIR/configs/tunnel.json

chmod +x $INSTALL_DIR/iron.py
ln -sf $INSTALL_DIR/iron.py /usr/local/bin/iron-tunnel

echo "[✓] Iron Tunnel installed"
echo "Run: iron-tunnel"
