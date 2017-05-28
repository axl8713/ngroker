'''
Created on Mar 12, 2017

@author: aleric
'''

import logging
import requests
import subprocess
import time
import os
from distutils.spawn import find_executable
from ngroker_config import Ngroker_Config

logger = logging.getLogger(__name__)

class Tunnel(object):
    def __init__(self, protocol=None, port=None, name=None, public_url=None):
    self.name = name
    self.port = port
    self.public_url = public_url
    self.protocol = protocol

    def __repr__(self):
        return "Tunnel " + self.name + " " + self.public_url if self.public_url != None else "Tunnel not open yet."

class Ngroker(object):

    def __init__(self):
    print Ngroker_Config.ngrok_api_url

    is_ngrok_started = False

    def start(self):

        if not self.is_ngrok_started:
            try:
                ngrok_exec_path = os.path.join(Ngroker_Config.exec_path,"ngrok")
                self._ngrok = subprocess.Popen(
                [ngrok_exec_path, "start", "-config="+os.path.join(Ngroker_Config.exec_path,"ngrok.yml"), "--none", "-region=eu"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except OSError as oserr:
                raise IOError("ngrok executable not found.")

        # maybe not needed
        time.sleep(1);

        if self._ngrok.poll() is None:
            self.is_ngrok_started = True
            logger.info("ngrok started.")
        else:
            raise ValueError("ngrok is not running.")

    def stop(self):
        if self._ngrok.poll() is None:
            logger.info("stopping ngrok client...")
            self._ngrok.terminate()
            self.is_ngrok_started = False
            logger.info("ngrok client stopped")
        else:
            raise ValueError("ngrok is not running.")

    def open_tunnel(self, protocol, port, name):

        logger.debug("Opening ngrok %s tunnel '%s' for port %d", protocol, name, port)

        # TODO: disable inspection!
        post = requests.post(Ngroker_Config.ngrok_api_url, json = {'addr':str(port), 'proto':str(protocol), 'name':str(name)})

        try:
            post.raise_for_status()

            public_url = post.json()['public_url']

            return Tunnel(protocol, port, name, public_url)

        except requests.exceptions.HTTPError as heerr:
            logger.error("error in opening the tunnel: %s", post.content)
            raise heerr

    def close_tunnel(self, name):

        logger.debug("Closing ngrok tunnel '%s'", name)
        delete = requests.delete(Ngroker_Config.ngrok_api_url + "/" + str(name))

        try:
            delete.raise_for_status()
            logger.debug("Tunnel closed")

        except requests.exceptions.HTTPError as heerr:
            logger.error("error in closing the tunnel: %s", delete.content)
            raise heerr
