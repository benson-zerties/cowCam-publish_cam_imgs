#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import pathlib
import io
import time
import janus
import asyncio
from queue import Queue
from zmq.asyncio import Context
from PIL import Image, UnidentifiedImageError
import requests

from requests_file import FileAdapter
from publishing_server import PublishingServer
from zmq_msg_detection_result import *

logger = logging.getLogger('appLogger')

async def capture_image(screen_capture_url, q, period_s):
    requests_s = requests.Session()
    requests_s.mount('file://', FileAdapter())
    while True:
        try:
            # capture image from camera with timeout 5s
            r = requests_s.get(screen_capture_url, timeout=5)
        except Exception as e:
            # re-create the requests session
            requests_s = requests.Session()
            requests_s.mount('file://', FileAdapter())
            print(e)
        else:
            # run if try did not raise exception
            if r:
                logger.debug('captured image')
                # create message
                msg = ZmqMsgDetectionResult()
                msg.header = b''
                msg.image = r.content
                msg.timestamp = bytes(str(int(time.time())), encoding='utf-8')
                msg.result = b''
                q.put_nowait(msg)
        await asyncio.sleep(period_s)

def io_main(qout: Queue, bind_addr: str):
    ctx = Context.instance()
    # setup out-broadcaster
    b = PublishingServer(bind_addr, qout, ctx)
    return b

async def main(img_src: str, bind_addr: str, period_s: int):
    queue_out = janus.Queue()
    # start io co-routines
    b = io_main(queue_out.async_q, bind_addr)
        
    img_capture = capture_image(img_src, queue_out.async_q, period_s)
    loop = asyncio.get_event_loop()
    loop.create_task(img_capture)
    
    while True:
        #queue_out.async_q.put_nowait('asdf')
        await asyncio.sleep(1)
    print('all tasks done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind_addr', type=str, help="Specify the ddress and port to listen to", )
    parser.add_argument('-p', '--period', type=int, default=60, 
            help="Specify period between taking images in seconds")
    parser.add_argument('-s', '--client_stale_timeout', type=int, default=60, 
            help="Specify period until clients are removed from list")
    parser.add_argument('-u', '--capture_url', type=str, help="Specify the image capturing url")
    args = parser.parse_args()

    model_path = pathlib.Path('..','model')

    logging.basicConfig(
        #filename = "cam_handler_remote.log",
        stream = sys.stdout,
        level = logging.DEBUG,
        filemode = "a",
        format = "%(asctime)s %(funcName)s Line:%(lineno)s [%(levelname)-8s] %(message)s",
        datefmt = "%H:%M:%S")

    asyncio.run(main(args.capture_url, args.bind_addr, args.period))
