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
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass


async def handle_client(local_reader, local_writer, target_host, target_port):
    peer = local_writer.get_extra_info("peername")
    print(f"[+] Incoming connection from {peer}")

    try:
        remote_reader, remote_writer = await asyncio.open_connection(
            target_host, target_port
        )
        print(f"[→] Connected to target {target_host}:{target_port}")

        await asyncio.gather(
            pipe(local_reader, remote_writer),
            pipe(remote_reader, local_writer)
        )

    except Exception as e:
        print(f"[!] Connection error: {e}")

    finally:
        try:
            local_writer.close()
            await local_writer.wait_closed()
        except:
            pass


async def start_server(listen_port, target_host, target_port):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, target_host, target_port),
        host="0.0.0.0",
        port=listen_port
    )

    print(f"[✓] Listening on 0.0.0.0:{listen_port}")
    print(f"[→] Forwarding to {target_host}:{target_port}")

    async with server:
        await server.serve_forever()
