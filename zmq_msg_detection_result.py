#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from zmq_msg_multi_part import *

class ZmqMsgDetectionResult(ZmqMsgMultiPart):

    image = b""
    result   = b""
    timestamp = b""
