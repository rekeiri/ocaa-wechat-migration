import asyncio
from aiofile import AIOFile

async def writeline_to_log_async(text):
    async with AIOFile("./logs/alog.txt", "a+",) as afp:
        await afp.write(text+"\n")
        await afp.fsync()