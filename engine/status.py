import asyncio
import time

STATUS = {}

async def check(target):
    STATUS[target] = "CHECKING"
    h,p = target.split(":")
    try:
        r,w = await asyncio.wait_for(asyncio.open_connection(h,int(p)),2)
        w.close()
        await w.wait_closed()
        STATUS[target] = "CONNECTED"
    except:
        STATUS[target] = "DEAD"

async def status_loop(targets):
    while True:
        await asyncio.gather(*(check(t) for t in targets))
        await asyncio.sleep(5)

def get_status(t):
    return STATUS.get(t,"UNKNOWN")
