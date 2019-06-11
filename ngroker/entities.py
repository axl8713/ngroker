'''
Created on Mar 12, 2017

@author: aleric
'''

import logging

logger = logging.getLogger(__name__)


class Tunnel(object):
    def __init__(self, protocol=None, port=None, name=None, public_url=None):
        self.name = name
        self.port = port
        self.public_url = public_url
        self.protocol = protocol

    def __repr__(self):
        return "Tunnel " + self.name + " " + self.public_url if self.public_url != None else "Tunnel not open yet."
