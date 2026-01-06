import websockets

from CONST import MESSAGE_SIZE


class Message:

    def __init__(self, ws: websockets.WebSocketClientProtocol):
        self.buffer = bytearray(MESSAGE_SIZE)
        self.offset = 0
        self.ws = ws

    async def add(self, data: bytearray) -> None:
        size_data = len(data)
        if self.offset + size_data > MESSAGE_SIZE:
            await self.flush()
        self.buffer[self.offset:self.offset + size_data] = data
        self.offset += size_data

    async def flush(self) -> None:
        if self.offset == 0:
            return
        await self.ws.send(self.buffer[:self.offset])
        self.offset = 0
