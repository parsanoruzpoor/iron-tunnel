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
mkdir -p $INSTALL_DIR/configs

echo "[*] Downloading Iron Tunnel files..."

# ---- MAIN APP ----
curl -fsSL $BASE_URL/iron.py -o $INSTALL_DIR/iron.py

# ---- ENGINE ----
curl -fsSL $BASE_URL/engine/proxy.py -o $INSTALL_DIR/engine/proxy.py
curl -fsSL $BASE_URL/engine/status.py -o $INSTALL_DIR/engine/status.py
curl -fsSL $BASE_URL/engine/__init__.py -o $INSTALL_DIR/engine/__init__.py

# ---- DEFAULT CONFIG ----
if [[ ! -f "$INSTALL_DIR/configs/tunnel.json" ]]; then
cat <<EOF > $INSTALL_DIR/configs/tunnel.json
{
  "mode": "iran",
  "listen": "0.0.0.0:0",
  "targets": []
}
EOF
fi

chmod +x $INSTALL_DIR/iron.py

ln -sf $INSTALL_DIR/iron.py /usr/local/bin/iron-tunnel

echo
echo "[✓] Iron Tunnel installed successfully"
echo "Run: iron-tunnel"
