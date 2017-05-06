'''
Created on Mar 12, 2017

@author: aleric
'''
import time
import logging
import telegram_bot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    telegram_bot.Telegram_bot()

    while True:
        time.sleep(2)
