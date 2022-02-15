#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC

class ZmqMsgMultiPart(ABC):

    header = b''

    def __init__(self, *args, **kwargs):
        self.header = args[0] if args else None
        self.__dict__.update(kwargs)

#    @property
#    def data(self):
#        print('obtaining data')
#        print(self.__dict__)
#        return [ x for x in self.__dict__ ]

    @classmethod
    def recv(cls, socket):
        """
        Reads key-value message from socket, returns new instance.
        """
        return cls.from_msg(socket.recv_multipart())

    @classmethod
    def from_msg(cls, msg):
        # filter out dunter name and filter for attributes
        # attributes are ordered according to definition, see PEP520
        tmp = [name for name in cls.__dict__ if isinstance(cls.__dict__[name], bytes) and not
                                                (name.startswith('__') and name.endswith('__'))]
        a = {k:cls.__dict__[k] for k in tmp}
        # assign message parts to attributes
        for idx,k in enumerate(a):
            a[k] = msg[idx+1]
        # Construct a FileMessage from a pyzmq message
        return cls(msg[0], **a)

    @property
    def msg(self):
        return [ d for d in self.__dict__.values() ]

    def send(self, socket, identity=None):
        """
        Send message to socket
        """
        msg = self.msg
        if identity:
            msg = [ identity ] + msg
        #print(msg)
        socket.send_multipart(msg)
