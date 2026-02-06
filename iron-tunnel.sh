#!/bin/bash
set -e

INSTALL_DIR="/opt/iron-tunnel"
BASE_URL="https://raw.githubusercontent.com/parsanoruzpoor/iron-tunnel/main"

# -------- ROOT CHECK --------
if [[ $EUID -ne 0 ]]; then
  echo "[!] Please run as root"
  exit 1
fi

echo "[*] Installing dependencies..."
apt update -y
apt install -y python3 python3-pip curl

echo "[*] Preparing directories..."
mkdir -p $INSTALL_DIR/engine

echo "[*] Downloading Iron Tunnel..."
curl -fsSL $BASE_URL/iron-tunnel.py -o $INSTALL_DIR/iron-tunnel.py
curl -fsSL $BASE_URL/engine/proxy.py -o $INSTALL_DIR/engine/proxy.py
curl -fsSL $BASE_URL/engine/__init__.py -o $INSTALL_DIR/engine/__init__.py || true

chmod +x $INSTALL_DIR/iron-tunnel.py

ln -sf $INSTALL_DIR/iron-tunnel.py /usr/local/bin/iron-tunnel

echo
echo "[✓] Iron Tunnel installed successfully"
echo "Run: iron-tunnel"
