# TCPip.py
# 1/11/2022
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The TCP Server loop. It runs in parallel with the Command Handler and
# Transmit loops. This loop accepts multiple simultaneous connections
# and passes incoming data to the Command Queue, which is picked up by the
# Command Handler.

import logging
import asyncio
from asyncio.exceptions import IncompleteReadError

class TCPServer():
    def __init__(self, hostname, port):
        self.logger = logging.getLogger('stages')
        self.qCmd = asyncio.Queue()
        self.qXmit = asyncio.Queue()
        self.hostname = hostname
        self.port = port
    
    async def start(self):
        server = await asyncio.start_server(
            client_connected_cb=self.cmd_loop, 
            host=self.hostname, 
            port=self.port)
        addr = server.sockets[0].getsockname()
        self.logger.info('listening on: %s', addr)

        async with server:
            await server.serve_forever()

    def stopped(self):
        self.logger.info('Server Stopped')

    async def cmd_loop(self, reader, writer):
        request = None
        cmdLoopCheck = True
        addr = writer.get_extra_info('peername')
        self.logger.info(f'new connection: {addr!r}')
                
        while cmdLoopCheck:        
            try:
                if writer.is_closing():
                    cmdLoopCheck = False
                else:
                    data = await reader.readuntil(separator=b'\n')
                    message = data.decode()
                    self.logger.info(f'received: {message!r} from {addr!r}')
                    
                    if message.lower() == 'q\r\n':
                        cmdLoopCheck = False
                        asyncio.create_task(self.enqueue_xmit((writer, 'closing connection...\n')))
                        await asyncio.sleep(0.001)
                    else:
                        asyncio.create_task(self.enqueue_cmd((writer, message)))
                        await writer.drain()

            except IncompleteReadError as e3:
                self.logger.error(f'Warning: peer disconnected')
                cmdLoopCheck = False
                await writer.drain()
                writer.close()

            except Exception as e2:
                self.logger.error(f'Unexpected error: {e2}')
                await writer.drain()

        if not writer.is_closing():
            await writer.drain()
            writer.close()

    async def enqueue_cmd(self, message):
        await self.qCmd.put(message)

    async def enqueue_xmit(self, message):
        await self.qXmit.put(message)