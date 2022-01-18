# cmdHandler.py
# 1/11/2022
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Command Handler loop. Runs in parallel with the TCP Server and
# Transmit loops. It constantly monitors the Command Queue and 
# acts upon new commands in the order they are received.

import logging
import asyncio
import time
import queue

class CMDLoop:
    def __init__(self, qCmd, qXmit, openDevs):
        self.log = logging.getLogger('stages')
        self.qCmd = qCmd
        self.qXmit = qXmit
        self.qUDP = queue.Queue()
        self.axis_a = openDevs[0]
        self.axis_b = openDevs[1]
        self.axis_c = openDevs[2]
        self.axis_d = openDevs[3]

    async def start(self):
        lastTime = 0
        while True:
            newTime = time.perf_counter()
            # if lastTime == 0:
            #     tempTime = newTime - 1

            ### Check the Command Queue ###
            if not self.qCmd.empty():
                msg = await self.qCmd.get()
                writer = msg[0]
                cmd = msg[1]

                retData = await self.parse_raw_command(cmd)
                await self.enqueue_xmit((writer, retData+'\n'))

            lastTime = newTime
            await asyncio.sleep(0.000001)

    async def parse_raw_command(self, rawCmd):
        cmdStr = rawCmd.strip()  # remove whitespace at the end
        
        if len(cmdStr) != 0:
            # cmdStr = cmdStr.replace(' ', '')  # Remove all whitespace
            cmdStrList = cmdStr.split(',')  # split the command on the commas
            retData = await self.execute_command(cmdStrList)
        else:
            retData = 'BAD,command failure: empty command'
            self.log.error(retData)

        #if 'BAD' not in retData and 'OK' not in retData:
        #    retData = 'OK,'+retData

        return retData

    async def execute_command(self, cmdStrList):
        cmd = cmdStrList[0]
        args = cmdStrList[1:]
        retData = 'OK'

        try:
            # Handle each command case
            if cmd == 'status':
                ## get status(es)
                ## loop through remaining items of cmdStrList
                if len(args) != 0:
                    for dev in args:
                        if dev == 'a':
                            result_a1 = self.axis_a.get_move_status()
                            result_a2 = self.axis_a.get_position()
                            
                            if 'BAD' not in result_a1 and 'BAD' not in result_a2:
                                units_a = self.axis_a.units
                                retData += f'\na={result_a1[1]}, {result_a2[1]}{units_a}'
                            else:
                                retData += f'\nBAD'
                                
                        elif dev == 'b':
                            result_b1 = self.axis_b.get_move_status()
                            result_b2 = self.axis_b.get_position()
                            
                            if 'BAD' not in result_b1 and 'BAD' not in result_b2:
                                units_b = self.axis_b.units
                                retData += f'\nb={result_b1[1]}, {result_b2[1]}{units_b}'
                            else:
                                retData += f'\nBAD'

                        elif dev == 'c':
                            result_c1 = self.axis_c.get_move_status()
                            result_c2 = self.axis_c.get_position()
                            
                            if 'BAD' not in result_c1 and 'BAD' not in result_c2:
                                units_c = self.axis_c.units
                                retData += f'\nc={result_c1[1]}, {result_c2[1]}{units_c}'
                            else:
                                retData += f'\nBAD'

                        elif dev == 'd':
                            result_d1 = self.axis_d.get_move_status()
                            result_d2 = self.axis_d.get_position()
                            
                            if 'BAD' not in result_d1 and 'BAD' not in result_d2:
                                units_d = self.axis_d.units
                                retData += f'\nd={result_d1[1]}, {result_d2[1]}{units_d}'
                            else:
                                retData += f'\nBAD'
                        else:
                            retData = 'BAD, invalid stage selection'
                else:
                    result_a1 = self.axis_a.get_move_status()
                    result_a2 = self.axis_a.get_position()
                    units_a = self.axis_a.units
                    retData += f'\na={result_a1[1]}, {result_a2[1]}{units_a}'

                    result_b1 = self.axis_b.get_move_status()
                    result_b2 = self.axis_b.get_position()
                    units_b = self.axis_b.units
                    retData += f'\nb={result_b1[1]}, {result_b2[1]}{units_b}'

                    result_c1 = self.axis_c.get_move_status()
                    result_c2 = self.axis_c.get_position()
                    units_c = self.axis_c.units
                    retData += f'\nc={result_c1[1]}, {result_c2[1]}{units_c}'

                    result_d1 = self.axis_d.get_move_status()
                    result_d2 = self.axis_d.get_position()
                    units_d = self.axis_d.units
                    retData += f'\nd={result_d1[1]}, {result_d2[1]}{units_d}'
            
            elif cmd == 'state':
                ## get move state
                state = 'IDLE'
                result_a = self.axis_a.get_move_status()
                result_b = self.axis_b.get_move_status()
                result_c = self.axis_c.get_move_status()
                result_d = self.axis_d.get_move_status()

                if 'BUSY' in result_a or 'BUSY' in result_b or \
                    'BUSY' in result_c or 'BUSY' in result_d:
                    state = 'BUSY'

                retData += f',{state}'

            elif cmd == 'stop':
                if len(args) != 0:
                    for dev in args:
                        if dev[0:2] == 'a':
                            result_a = self.axis_a.stop()

                            if 'BAD' not in result_a:
                                retData += f'\n{result_a}'
                            else:
                                retData += f'\nBAD'
                                
                        elif dev[0:2] == 'b':
                            result_b = self.axis_b.stop()

                            if 'BAD' not in result_b:
                                retData += f'\n{result_b}'
                            else:
                                retData += f'\nBAD'

                        elif dev[0:2] == 'c':
                            result_c = self.axis_c.stop()

                            if 'BAD' not in result_c:
                                retData += f'\n{result_c}'
                            else:
                                retData += f'\nBAD'

                        elif dev[0:2] == 'd':
                            result_d = self.axis_d.stop()

                            if 'BAD' not in result_d:
                                retData += f'\n{result_d}'
                            else:
                                retData += f'\nBAD'
                        else:
                            retData = 'BAD, invalid stage selection'
                else:
                    retData = 'BAD, invalid move command'

                retData = 'OK'

            elif cmd == 'home':
                if len(args) != 0:
                    for dev in args:
                        if dev == 'a':
                            result_a = self.axis_a.home()
                            if 'BAD' not in result_a:
                                retData = retData + '\n' + result_a
                            else:
                                retData = retData + '\nBAD'
                                
                        elif dev == 'b':
                            result_b = self.axis_b.home()
                            if 'BAD' not in result_b:
                                retData = retData + '\n' + result_b
                            else:
                                retData = retData + '\nBAD'

                        elif dev == 'c':
                            result_c = self.axis_c.home()
                            if 'BAD' not in result_c:
                                retData = retData + '\n' + result_c
                            else:
                                retData = retData + '\nBAD'

                        elif dev == 'd':
                            result_d = self.axis_d.home()
                            if 'BAD' not in result_d:
                                retData = retData + '\n' + result_d
                            else:
                                retData = retData + '\nBAD'
                        else:
                            retData = 'BAD, invalid stage selection'
                else:
                    result_a = self.axis_a.home()
                    result_b = self.axis_b.home()
                    result_c = self.axis_c.home()
                    result_d = self.axis_d.home()

            elif cmd == 'goto' or cmd == 'offset':
                if len(args) != 0:
                    for dev in args:
                        if dev[0:2] == 'a=':
                            try:
                                val = float(dev[2:])
                                if cmd == 'goto':
                                    result_a = self.axis_a.goto_real(val)
                                elif cmd == 'offset':
                                    result_a = self.axis_a.offset_real(val)

                                if 'BAD' not in result_a:
                                    retData += f'\n{result_a}'
                                else:
                                    retData += f'\nBAD'
                            except ValueError as e:
                                retData = f'BAD, command failure: expected args float or int = {e}'
                                self.log.error(retData)
                                return retData
                                
                        elif dev[0:2] == 'b=':
                            try:
                                val = float(dev[2:])
                                if cmd == 'goto':
                                    result_b = self.axis_b.goto_real(val)
                                elif cmd == 'offset':
                                    result_b = self.axis_b.offset_real(val)

                                if 'BAD' not in result_b:
                                    retData += f'\n{result_b}'
                                else:
                                    retData += f'\nBAD'
                            except ValueError as e:
                                retData = f'BAD, command failure: expected args float or int = {e}'
                                self.log.error(retData)
                                return retData

                        elif dev[0:2] == 'c=':
                            try:
                                val = float(dev[2:])
                                if cmd == 'goto':
                                    result_c = self.axis_c.goto_real(val)
                                elif cmd == 'offset':
                                    result_c = self.axis_c.offset_real(val)
                                    
                                if 'BAD' not in result_c:
                                    retData += f'\n{result_c}'
                                else:
                                    retData += f'\nBAD'
                            except ValueError as e:
                                retData = f'BAD, command failure: expected args float or int = {e}'
                                self.log.error(retData)
                                return retData

                        elif dev[0:2] == 'd=':
                            try:
                                val = float(dev[2:])
                                if cmd == 'goto':
                                    result_d = self.axis_d.goto_real(val)
                                elif cmd == 'offset':
                                    result_d = self.axis_d.offset_real(val)

                                if 'BAD' not in result_d:
                                    retData += f'\n{result_d}'
                                else:
                                    retData = retData + '\nBAD'
                            except ValueError as e:
                                retData = f'BAD, command failure: expected args float or int = {e}'
                                self.log.error(retData)
                                return retData
                        else:
                            retData = 'BAD, invalid stage selection'
                else:
                    retData = 'BAD, invalid move command'

                retData = 'OK'
                
            else:
                retData = f'BAD,command failure: unknown command {cmd!r}'
                self.log.error(retData)
                return retData

            return retData
        
        except (TypeError, ValueError) as e:
            retData = f'BAD,command failure: expected args float or int = {e}'
            self.log.error(retData)
            return retData

    async def enqueue_xmit(self, msg):
        await self.qXmit.put(msg)

    def enqueue_udp(self, msg):
        self.qUDP.put(msg)