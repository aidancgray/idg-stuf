# transmitter.py
# 1/11/2022
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The Transmit Loop. It runs in parallel with the Command Handler and 
# TCP Server loops. It monitors the Transmit Queue for new messages, 
# then sends out the message to the correct client.

import logging

class Transmitter:
    def __init__(self, qXmit):
        self.logger = logging.getLogger('stages')
        self.qXmit = qXmit

    async def start(self):
        while True:
            cmd = await self.qXmit.get()  
            writer = cmd[0]
            msg = cmd[1]
            if not writer.is_closing():
                addr = writer.get_extra_info('peername')
                self.logger.info(f'sending: {msg!r} to {addr!r}')
                writer.write(msg.encode())
                await writer.drain()
            else:
                self.logger.warn(f'Warning: peer disconnected')