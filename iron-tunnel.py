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
    print("=== Create Tunnel ===\n")

    mode = input("Mode (iran/kharej): ").strip().lower()
    if mode not in ("iran", "kharej"):
        print("Invalid mode")
        input("Press Enter...")
        return

    listen_port = input("Listen Port (empty = auto): ").strip()
    if listen_port:
        if not listen_port.isdigit():
            print("Invalid port")
            return
        listen_port = int(listen_port)
    else:
        listen_port = find_free_port()

    config = {
        "mode": mode,
        "listen_port": listen_port
    }

    if mode == "iran":
        kh_ip = input("Kharej Server IP: ").strip()
        kh_port = input("Kharej Tunnel Port: ").strip()
        if not kh_port.isdigit():
            print("Invalid port")
            return
        config["kharej_ip"] = kh_ip
        config["kharej_port"] = int(kh_port)

    else:  # kharej
        out_port = input("Outbound (VLESS) Port [127.0.0.1]: ").strip()
        if not out_port.isdigit():
            print("Invalid port")
            return
        config["outbound_port"] = int(out_port)

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print("\n[✓] Tunnel created")
    input("Press Enter...")

# ---------------- RUN TUNNEL ----------------
def run_tunnel():
    if not os.path.exists(CONFIG_FILE):
        print("No config found.")
        return

    with open(CONFIG_FILE) as f:
        cfg = json.load(f)

    mode = cfg["mode"]
    listen_port = cfg["listen_port"]

    from engine.proxy import start_server

    if mode == "iran":
        target_ip = cfg["kharej_ip"]
        target_port = cfg["kharej_port"]
    else:
        target_ip = "127.0.0.1"
        target_port = cfg["outbound_port"]

    clear()
    logo()
    print(f"Mode   : {mode}")
    print(f"Listen : 0.0.0.0:{listen_port}")
    print(f"Target : {target_ip}:{target_port}")
    print("\n[CTRL+C to stop]\n")

    asyncio.run(
        start_server(
            listen_port,
            target_ip,
            target_port
        )
    )

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

    targets = cfg.get("targets", [])
    if not targets:
        print("No targets defined in config.")
        input("Press Enter...")
        return

    for t in targets:
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
