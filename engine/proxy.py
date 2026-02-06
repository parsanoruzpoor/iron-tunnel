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


class TunnelServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handle(self, r, w):
        await pipe(r, w)

    async def start(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)
        print(f"[✓] Kharej listening on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


class TunnelClient:
    def __init__(self, lhost, lport, rhost, rport):
        self.lhost = lhost
        self.lport = lport
        self.rhost = rhost
        self.rport = rport

    async def handle(self, lr, lw):
        rr, rw = await asyncio.open_connection(self.rhost, self.rport)
        await asyncio.gather(
            pipe(lr, rw),
            pipe(rr, lw)
        )

    async def start(self):
        server = await asyncio.start_server(self.handle, self.lhost, self.lport)
        print(f"[✓] Iran listening on {self.lhost}:{self.lport}")
        print(f"[→] Tunnel to {self.rhost}:{self.rport}")
        async with server:
            await server.serve_forever()
