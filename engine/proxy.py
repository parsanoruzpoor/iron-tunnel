import asyncio
import random

class TCPProxy:
    def __init__(self, listen_port, outbound_ports):
        self.listen_port = listen_port
        self.outbound_ports = outbound_ports

    async def pipe(self, reader, writer):
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except:
            pass
        finally:
            writer.close()

    async def handle(self, client_reader, client_writer):
        port = random.choice(self.outbound_ports)

        try:
            remote_reader, remote_writer = await asyncio.open_connection(
                "127.0.0.1", port
            )
        except:
            client_writer.close()
            return

        await asyncio.gather(
            self.pipe(client_reader, remote_writer),
            self.pipe(remote_reader, client_writer)
        )

    async def start(self):
        server = await asyncio.start_server(
            self.handle, "0.0.0.0", self.listen_port
        )
        async with server:
            await server.serve_forever()
