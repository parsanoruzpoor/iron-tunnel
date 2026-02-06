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
    finally:
        writer.close()
        await writer.wait_closed()

class TCPProxy:
    def __init__(self, host, port, targets):
        self.host = host
        self.port = port
        self.targets = targets
        self.idx = 0

    def pick_target(self):
        t = self.targets[self.idx % len(self.targets)]
        self.idx += 1
        h,p = t.split(":")
        return h,int(p)

    async def handle(self, r, w):
        h,p = self.pick_target()
        rr,rw = await asyncio.open_connection(h,p)
        await asyncio.gather(
            pipe(r,rw),
            pipe(rr,w)
        )

    async def start(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)
        async with server:
            await server.serve_forever()
