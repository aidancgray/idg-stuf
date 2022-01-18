# UDPcast.py
# 1/11/2022
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The UDP Broadcast Loop. The Command Handler puts messages on the qUDP queue,
# which are then broadcast on the given ip (which is set in main.py and should
# end in 255, ie. 192.168.1.255).

import asyncio
import logging
import socket
from typing import Tuple, Union, Text

Address = Tuple[str, int]

class BroadcastProtocol(asyncio.DatagramProtocol):

    def __init__(self, qUDP, target: Address, *, loop: asyncio.AbstractEventLoop = None):
        self.logger = logging.getLogger('stages')
        self.qUDP = qUDP
        self.target = target
        self.loop = asyncio.get_event_loop() if loop is None else loop

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self.transport = transport
        sock = transport.get_extra_info("socket")  # type: socket.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast()

    def datagram_received(self, data: Union[bytes, Text], addr: Address):
        #self.logger.info(f'data received: {data} {addr}')
        pass

    def broadcast(self):
        if not self.qUDP.empty():
            msg = self.qUDP.get()  
            #self.logger.info(f'sending {msg} to {self.target}')
            self.transport.sendto(msg.encode(), self.target)
        self.loop.call_soon(self.broadcast)

class UDPcast:
    def __init__(self, hostname, port, qUDP):
        self.hostname = hostname
        self.port = port
        self.qUDP = qUDP

    async def start(self):
        loop = asyncio.get_event_loop()
        udpTask = loop.create_datagram_endpoint(
                lambda: BroadcastProtocol(self.qUDP, (self.hostname, self.port), loop=loop), 
                local_addr=('0.0.0.0', self.port))
        await udpTask