import asyncio

BUFFER = 65536

async def pipe(reader, writer):
    try:
        while True:
            data = await reader.read(BUFFER)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except:
        pass
    finally:
        writer.close()

class TCPProxy:
    def __init__(self, listen_host, listen_port, targets, mode):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.targets = targets
        self.mode = mode

    async def handle_client(self, local_reader, local_writer):
        # ---- IRAN ----
        if self.mode == "iran":
            target = self.targets[0]  # kharej ip:port
        # ---- KHAREJ ----
        else:
            target = self.targets[0]  # local service port (مثلاً 127.0.0.1:443)

        host, port = target.split(":")
        port = int(port)

        try:
            remote_reader, remote_writer = await asyncio.open_connection(host, port)
            print(f"[→] Forwarding to {host}:{port}")

            await asyncio.gather(
                pipe(local_reader, remote_writer),
                pipe(remote_reader, local_writer)
            )
        except Exception as e:
            print(f"[!] Tunnel error: {e}")
            local_writer.close()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client,
            host=self.listen_host,
            port=self.listen_port
        )

        role = "Iran" if self.mode == "iran" else "Kharej"
        print(f"[✓] {role} listening on {self.listen_host}:{self.listen_port}")

        async with server:
            await server.serve_forever()
