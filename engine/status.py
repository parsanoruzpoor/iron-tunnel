import socket
import time

def get_status(target, timeout=2):
    host, port = target.split(":")
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return "CONNECTED"
    except:
        return "DEAD"
