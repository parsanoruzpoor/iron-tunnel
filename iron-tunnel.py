#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import socket

BASE_DIR = "/opt/iron-tunnel"
CONFIG_FILE = f"{BASE_DIR}/configs/tunnel.json"

sys.path.insert(0, BASE_DIR)

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

def test_target(target, timeout=3):
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
    status = connection_status()
    print(f"""
[ Status: {status} ]

[1] Create Tunnel
[2] Run Tunnel
[3] Show Config
[4] Test Connection
[0] Exit
""")

# ---------------- CREATE TUNNEL ----------------
def create_tunnel():
    clear()
    logo()
    print("=== Create New Tunnel ===\n")

    mode = input("Mode (iran/kharej): ").strip().lower()
    if mode not in ("iran", "kharej"):
        print("Invalid mode")
        input("Press Enter...")
        return

    listen_ip = input("Listen IP (0.0.0.0): ").strip() or "0.0.0.0"

    pref = input("Preferred Listen Port (e.g. 443, empty = auto): ").strip()
    if pref:
        if not pref.isdigit():
            print("Invalid port")
            input("Press Enter...")
            return
        pref = int(pref)
        if is_port_free(pref, listen_ip):
            listen_port = pref
        else:
            suggested = find_free_port()
            print(f"\nPort {pref} is busy.")
            print(f"Suggested free port: {suggested}")
            yn = input("Use suggested port? (Y/n): ").strip().lower()
            if yn == "n":
                print("Canceled.")
                input("Press Enter...")
                return
            listen_port = suggested
    else:
        listen_port = find_free_port()
        print(f"Auto-selected free port: {listen_port}")

    try:
        count = int(input("\nHow many outbound targets? "))
        if count <= 0:
            raise ValueError
    except:
        print("Invalid number")
        input("Press Enter...")
        return

    targets = []
    for i in range(count):
        ip = input(f"Target {i+1} IP: ").strip()
        port = input(f"Target {i+1} Port: ").strip()
        if not port.isdigit():
            print("Invalid target port")
            input("Press Enter...")
            return
        targets.append(f"{ip}:{port}")

    config = {
        "mode": mode,
        "listen": f"{listen_ip}:{listen_port}",
        "targets": targets
    }

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print("\n[✓] Tunnel created successfully")
    print(f"Listening on: {listen_ip}:{listen_port}")
    input("Press Enter to return to menu...")

# ---------------- RUN TUNNEL ----------------
def run_tunnel():
    if not os.path.exists(CONFIG_FILE):
        print("No config found.")
        input("Press Enter...")
        return

    with open(CONFIG_FILE) as f:
        cfg = json.load(f)

    host, port = cfg["listen"].split(":")
    port = int(port)
    targets = cfg["targets"]

    from engine.proxy import TCPProxy

    clear()
    logo()
    print("[*] Tunnel running")
    print(f"[*] Listen: {host}:{port}")
    print("[*] Targets:")
    for t in targets:
        print(f"   - {t}")
    print("\n[CTRL+C to stop]\n")

    proxy = TCPProxy(host, port, targets)
    try:
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        print("\n[!] Tunnel stopped")
        input("Press Enter...")

# ---------------- SHOW / TEST ----------------
def show_config():
    clear()
    logo()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            print(f.read())
    else:
        print("No config found.")
    input("\nPress Enter...")

def test_connection_menu():
    clear()
    logo()
    print("=== Connection Test ===\n")
    if not os.path.exists(CONFIG_FILE):
        print("No config found.")
        input("Press Enter...")
        return

    with open(CONFIG_FILE) as f:
        cfg = json.load(f)

    for t in cfg["targets"]:
        print(f"{t} -> ", end="")
        print("CONNECTED" if test_target(t) else "FAILED")

    input("\nPress Enter...")

# ---------------- MAIN ----------------
def main():
    while True:
        clear()
        logo()
        menu()
        c = input("Select > ").strip()

        if c == "1":
            create_tunnel()
        elif c == "2":
            run_tunnel()
        elif c == "3":
            show_config()
        elif c == "4":
            test_connection_menu()
        elif c == "0":
            sys.exit(0)
        else:
            print("Invalid option")
            input("Press Enter...")

if __name__ == "__main__":
    main()
