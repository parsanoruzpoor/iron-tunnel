#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import socket

BASE_DIR = "/opt/iron-tunnel"
CONFIG_FILE = f"{BASE_DIR}/configs/tunnel.json"

sys.path.insert(0, BASE_DIR)

from engine.proxy import TCPProxy

# ---------------- UTILS ----------------
def clear():
    os.system("clear")

def is_port_free(port, host="0.0.0.0"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except:
        return False

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def test_target(target, timeout=2):
    host, port = target.split(":")
    port = int(port)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def connection_status():
    if not os.path.exists(CONFIG_FILE):
        return "NO CONFIG"
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    targets = cfg.get("targets", [])
    if not targets:
        return "NO TARGETS"
    ok = sum(1 for t in targets if test_target(t))
    if ok == 0:
        return "DISCONNECTED"
    elif ok < len(targets):
        return "PARTIAL"
    return "CONNECTED"

# ---------------- UI ----------------
def logo():
    print(r"""
██╗██████╗  ██████╗ ███╗   ██╗
██║██╔══██╗██╔═══██╗████╗  ██║
██║██████╔╝██║   ██║██╔██╗ ██║
██║██╔══██╗██║   ██║██║╚██╗██║
██║██║  ██║╚██████╔╝██║ ╚████║
╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
        IRON TUNNEL
""")

def menu():
    clear()
    logo()
    print(f"[ Tunnel Status: {connection_status()} ]\n")
    print("""
[1] Create Tunnel
[2] Run Tunnel
[3] Show Config
[4] Test Connection
[0] Exit
""")

# ---------------- CREATE ----------------
def create_tunnel():
    clear()
    logo()
    print("=== Create Tunnel ===\n")

    mode = input("Mode (iran/kharej): ").strip().lower()
    if mode not in ("iran","kharej"):
        input("Invalid mode..."); return

    listen_ip = "0.0.0.0"

    pref = input("Preferred listen port (empty = auto): ").strip()
    if pref and pref.isdigit() and is_port_free(int(pref)):
        listen_port = int(pref)
    else:
        listen_port = find_free_port()
        print(f"Auto port: {listen_port}")

    count = int(input("How many outbound targets? "))
    targets = []
    for i in range(count):
        ip = input(f"Target {i+1} IP: ").strip()
        port = input(f"Target {i+1} Port: ").strip()
        targets.append(f"{ip}:{port}")

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE,"w") as f:
        json.dump({"mode": mode, "listen": f"{listen_ip}:{listen_port}", "targets": targets}, f, indent=2)

    input("\n[✓] Tunnel created. Press Enter...")

# ---------------- RUN ----------------
def run_tunnel():
    if not os.path.exists(CONFIG_FILE):
        input("No config..."); return

    with open(CONFIG_FILE) as f:
        cfg = json.load(f)

    host, port = cfg["listen"].split(":")
    port = int(port)
    targets = cfg.get("targets", [])
    mode = cfg.get("mode","iran")

    proxy = TCPProxy(host, port, targets, mode)

    clear()
    logo()
    print("[*] Tunnel running (CTRL+C to stop)\n")
    try:
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        input("\nStopped. Press Enter...")

# ---------------- SHOW / TEST ----------------
def show_config():
    clear()
    logo()
    print(open(CONFIG_FILE).read() if os.path.exists(CONFIG_FILE) else "No config")
    input()

def test_connection_menu():
    clear()
    logo()
    if not os.path.exists(CONFIG_FILE):
        input("No config..."); return
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    for t in cfg.get("targets", []):
        print(f"{t} -> {'CONNECTED' if test_target(t) else 'FAILED'}")
    input()

# ---------------- MAIN ----------------
def main():
    while True:
        menu()
        c = input("Select > ").strip()
        if c=="1": create_tunnel()
        elif c=="2": run_tunnel()
        elif c=="3": show_config()
        elif c=="4": test_connection_menu()
        elif c=="0": sys.exit(0)

if __name__ == "__main__":
    main()
