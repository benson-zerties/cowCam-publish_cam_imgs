#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import asyncio
import queue
import zmq
from zmq.asyncio import Context

#from zmq_msg_detection_result import ZmqMsgDetectionResult

class PublishingServer(object):
    def __init__(self, bind_addr: str, qout: queue.Queue, ctx: Context):
        super().__init__()
        self._qout = qout
        self.ctx = ctx
        self.publisher = self.ctx.socket(zmq.PUB)
        self.publisher.bind(bind_addr)
        logging.info("Binding to %s" % (bind_addr))
        self._stop_event = asyncio.Event()
        # submit task to event loop
        loop = asyncio.get_event_loop()
        loop.create_task( self.broadcast() )

    def stop(self):
        self._stop_event.set()

    async def broadcast(self):
        while not self._stop_event.is_set():
            item = None
            try:
                msg = await self._qout.get()
            except queue.Empty as e:
                continue
            if msg is None:
                continue
            logging.info("Broadcasting")
            msg.send(self.publisher)
            self._qout.task_done()
