#!/usr/local/bin/python3.8
# demoScript.py
# 
# Demo script for the STUF stages.

import socket
import time
import logging
import sys
import argparse
import shlex

def send_cmd(log, s, cmd):
    #log.info(f'{cmd[:-2]}')
    s.sendall(cmd.encode())
    response = s.recv(1024).decode()[:-1]
    #log.info(f'{response}')
    #log.info(f'---')
    #time.sleep(0.1)

    return response

def demo_test(opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    log = logging.getLogger('demo')
    log.setLevel(opts.logLevel)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((opts.host, 1024))
        
        log.info('~~~ Starting STUF Stage Demo ~~~')
        while True:
            if 'BUSY' not in send_cmd(log, s, f'status,a\r\n'):
                send_cmd(log, s, f'goto,a=0\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,b\r\n'):
                send_cmd(log, s, f'goto,b=45\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,c\r\n'):
                send_cmd(log, s, f'goto,c=0\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,d\r\n'):
                send_cmd(log, s, f'goto,d=90\r\n')
            time.sleep(0.1)

            if 'BUSY' not in send_cmd(log, s, f'status,a\r\n'):
                send_cmd(log, s, f'goto,a=-180\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,b\r\n'):
                send_cmd(log, s, f'goto,b=-45\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,c\r\n'):
                send_cmd(log, s, f'goto,c=100\r\n')
            if 'BUSY' not in send_cmd(log, s, f'status,d\r\n'):
                send_cmd(log, s, f'goto,d=-90\r\n')
            time.sleep(0.1)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')
    parser.add_argument('--host', type=str, default='172.16.0.173',
                        help='the IP address to connect to')

    opts = parser.parse_args(argv)

    try:
        demo_test(opts)
    except KeyboardInterrupt:
        print('Exiting Program...')

if __name__ == "__main__":
    main()