#!/usr/bin/env python3
import os
import sys
import json
import socket
import asyncio

BASE = "/opt/iron-tunnel"
CFG = f"{BASE}/tunnel.json"

sys.path.insert(0, BASE)


def clear():
    os.system("clear")


def find_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def logo():
    print("""
██╗██████╗  ██████╗ ███╗   ██╗
██║██╔══██╗██╔═══██╗████╗  ██║
██║██████╔╝██║   ██║██╔██╗ ██║
██║██╔══██╗██║   ██║██║╚██╗██║
██║██║  ██║╚██████╔╝██║ ╚████║
╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
IRON TUNNEL
""")


def create():
    clear()
    logo()
    mode = input("Mode (iran/kharej): ").strip()

    if mode == "kharej":
        port = find_free_port()
        cfg = {"mode": "kharej", "listen": port}
        print(f"Kharej port: {port}")

    elif mode == "iran":
        ip = input("Kharej IP: ").strip()
        port = input("Kharej Port: ").strip()
        lport = find_free_port()
        cfg = {
            "mode": "iran",
            "listen": lport,
            "remote": f"{ip}:{port}"
        }
        print(f"Iran local port: {lport}")
    else:
        input("Invalid mode...")
        return

    os.makedirs(BASE, exist_ok=True)
    with open(CFG, "w") as f:
        json.dump(cfg, f, indent=2)

    input("\n[✓] Config saved. Enter...")


def run():
    if not os.path.exists(CFG):
        input("No config...")
        return

    from engine.proxy import TCPProxy


    with open(CFG) as f:
        cfg = json.load(f)

    clear()
    logo()

    try:
        if cfg["mode"] == "kharej":
            srv = TunnelServer("0.0.0.0", cfg["listen"])
            asyncio.run(srv.start())

        else:
            ip, port = cfg["remote"].split(":")
            cli = TunnelClient("0.0.0.0", cfg["listen"], ip, int(port))
            asyncio.run(cli.start())

    except KeyboardInterrupt:
        pass


def menu():
    while True:
        clear()
        logo()
        print("""
[1] Create Tunnel
[2] Run Tunnel
[0] Exit
""")
        c = input("> ").strip()
        if c == "1": create()
        elif c == "2": run()
        elif c == "0": sys.exit(0)


if __name__ == "__main__":
    menu()
