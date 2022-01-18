#!/usr/local/bin/python3.8
# main.py
# 1/11/2022
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The main script for the STUF Stages

import time
import os
import logging
import sys
import asyncio
import argparse
import shlex
import netifaces

from TCPip import TCPServer
from cmdHandler import CMDLoop
from transmitter import Transmitter
from UDPcast import UDPcast
from stageClass import Stage

CORRECTOR_ROTARY_SOFT_STOPS = (-180, 0) #deg
CORRECTOR_ROTARY_HOME_OFFSET = 900 #steps
CORRECTOR_ROTARY_CONVERSION_FACTOR = 0.00075
CORRECTOR_ROTARY_UNITS = "deg"

AOI_ROTARY_SOFT_STOPS = (-45, 45) #deg
AOI_ROTARY_HOME_OFFSET = -2900 #steps
AOI_ROTARY_CONVERSION_FACTOR = 0.00075
AOI_ROTARY_UNITS = "deg"

DMD_LINEAR_SOFT_STOPS = (0, 100) #mm
DMD_LINEAR_HOME_OFFSET = 500 #steps
DMD_LINEAR_CONVERSION_FACTOR = 0.00025
DMD_LINEAR_UNITS = "mm"

DMD_ROTARY_SOFT_STOPS = (0, 180) #deg
DMD_ROTARY_HOME_OFFSET = -1300 #steps
DMD_ROTARY_CONVERSION_FACTOR = 0.0005
DMD_ROTARY_UNITS = "deg"

def custom_except_hook(loop, context):
    if repr(context['exception']) == 'SystemExit()':
        log.info('Exiting Program...')

def open_devices():
    devList, devCount = scan_for_devices()
    openDevs = ['','','','']

    log.info("Number of devices = "+str(devCount))
    if devCount == 0:
        allDevCheck = False
    else:
        allDevCheck = True
        try:
            log.info("List of devices = ")

            for i in devList:
                log.info(repr(i))

                # Corrector Rotary Stage
                if '4A291' in repr(i):
                    axis_a = Stage(lib, i, "Corrector Rotary Stage",
                        CORRECTOR_ROTARY_SOFT_STOPS,
                        CORRECTOR_ROTARY_HOME_OFFSET,
                        CORRECTOR_ROTARY_CONVERSION_FACTOR,
                        CORRECTOR_ROTARY_UNITS)

                    if axis_a.stageDev > 0:
                        openDevs[0] = axis_a
                    else:
                        allDevCheck = False
                        log.error("BAD = Corrector Rotary Stage connection failed")

                # AOI Rotary Stage
                elif '4A321' in repr(i):
                    axis_b = Stage(lib, i, "AOI Rotary Stage",
                        AOI_ROTARY_SOFT_STOPS,
                        AOI_ROTARY_HOME_OFFSET,
                        AOI_ROTARY_CONVERSION_FACTOR,
                        AOI_ROTARY_UNITS)

                    if axis_b.stageDev > 0:
                        openDevs[1] = axis_b
                    else:
                        allDevCheck = False
                        log.error("BAD = AOI Rotary Stage connection failed")

                # DMD Linear Stage
                elif '4A221' in repr(i):
                    axis_c = Stage(lib, i, "DMD Linear Stage",
                        DMD_LINEAR_SOFT_STOPS,
                        DMD_LINEAR_HOME_OFFSET,
                        DMD_LINEAR_CONVERSION_FACTOR,
                        DMD_LINEAR_UNITS)

                    if axis_c.stageDev > 0:
                        openDevs[2] = axis_c
                    else:
                        allDevCheck = False
                        log.error("BAD = DMD Linear Stage connection failed")

                # DMD Rotary Stage
                elif '4A0C1' in repr(i):
                    axis_d = Stage(lib, i, "DMD Rotary Stage", \
                        DMD_ROTARY_SOFT_STOPS,
                        DMD_ROTARY_HOME_OFFSET,
                        DMD_ROTARY_CONVERSION_FACTOR,
                        DMD_ROTARY_UNITS)

                    if axis_d.stageDev > 0:
                        openDevs[3] = axis_d
                    else:
                        allDevCheck = False
                        log.error("BAD = DMD Rotary Stage connection failed")

        except IndexError:
            log.error("No devices to list...")

    return allDevCheck, openDevs

def scan_for_devices():
    """
    Scans for motor controllers on USB

    Returns the number and list of devices found
    """
    log.info("scanning for devices...")

    probe_flags = EnumerateFlags.ENUMERATE_PROBE
    devenum = lib.enumerate_devices(probe_flags, None)
    dev_count = lib.get_device_count(devenum)
    controller_name = controller_name_t()

    devices_list = []
    for dev_ind in range(0, dev_count):
        enum_name = lib.get_device_name(devenum, dev_ind)
        result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))

        if result == Result.Ok:
            devices_list.append(enum_name)

    return devices_list, dev_count

async def runStages(opts, openDevs):
    log.setLevel(opts.logLevel)
    log.info('starting logging')
    
    ip_address = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
    udp_address = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['broadcast']
    log.info(f'IP:  {ip_address}')
    log.info(f'UDP: {udp_address}')

    tcpServer = TCPServer(ip_address, 1024)
    cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit, openDevs)
    transmitter = Transmitter(tcpServer.qXmit)
    udpServer = UDPcast(udp_address, 8888, cmdHandler.qUDP)

    await asyncio.gather(tcpServer.start(), cmdHandler.start(), transmitter.start(), udpServer.start())

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')
    opts = parser.parse_args(argv)
    log.setLevel(opts.logLevel)

    allDevCheck, openDevs = open_devices()
    
    if allDevCheck:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(custom_except_hook)
        try:
            loop.run_until_complete(runStages(opts, openDevs))
        except KeyboardInterrupt:
            log.info('Exiting Program...')
    else:
        log.error("Terminating. Not all devices are available.")
        exit()

if __name__ == "__main__":
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    log = logging.getLogger('stages')

    # Set the current directory and get the path to pyximc.py
    cur_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ximcDir = (f'{cur_dir}/ximc-2.13.3/ximc')
    ximcPackageDir = os.path.join(ximcDir, "crossplatform", "wrappers", "python")
    sys.path.append(ximcPackageDir)

    try: 
        from pyximc import *
    except ImportError as err:
        log.error("Can't import pyximc module. The most probable reason is that you changed the relative location of the files..")
        exit()
        
    main()