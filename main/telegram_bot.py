import ngroker
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import time
import logging
import ConfigParser
import os

logger = logging.getLogger(__name__)

class Telegram_bot(object):

    def __init__(self):

        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ngroker.ini"))

        self._bot = telepot.Bot(self._config.get('telegram','bot_token'))
        self._bot.message_loop({'chat': self.handle_message, 'callback_query': self.on_callback_query})

        self._ngrok_client = ngroker.Ngroker()
        self._ngrok_client.start()

    def handle_message(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        try:
            if content_type == 'text':

                command = message['text'].upper();

                logger.debug("%s command received", command)

                if command == '/START':

                    self._ngrok_client.start()

                    keyboard = ReplyKeyboardMarkup(keyboard=[
                                     ['/open', '/stop'],
                    ])
                    self._bot.sendMessage(chat_id, 'Select a command', reply_markup=keyboard)

                elif command == '/OPEN':
                    if self._ngrok_client.is_ngrok_started:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [
                                InlineKeyboardButton(text='SSH', callback_data='ssh'),
                                InlineKeyboardButton(text='HTTP', callback_data='http'),
                                InlineKeyboardButton(text='manager', callback_data='manager_http')
                            ],
                        ])
                        self._bot.sendMessage(chat_id, 'Select tunnel type', reply_markup=keyboard)
                    else:
                        self._bot.sendMessage(chat_id, 'please start client first via /start')

                elif command == '/STOP':
                    self._ngrok_client.stop()
                    keyboard = ReplyKeyboardMarkup(keyboard=[
                                     ['/start'],
                    ])
                    self._bot.sendMessage(chat_id, 'Select /start command to start client', reply_markup=keyboard)
        except Exception as ex:
            logger.error("error in handling message: "+ str(ex))
            self._bot.sendMessage(chat_id, 'someting went wrong: '+ str(ex))

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        self._bot.answerCallbackQuery(query_id, text='opening ' + query_data + ' tunnel. stay tight.')

        if query_data=='manager_http':
            tunnel = self.open_manager_tunnel()
        elif query_data=='ssh':
            tunnel = self.open_ssh_tunnel()

        self._bot.sendMessage(from_id, str(tunnel))

    def open_manager_tunnel(self):

        protocol = 'http'
        port = 4040
        name = 'ngrok_manager'

        t = self._ngrok_client.open_tunnel(protocol, port, name)
        print t
        return t

    def open_ssh_tunnel(self):

        protocol = 'tcp'
        port = 22
        name = 'raspizero-ssh'

        tunnel = self._ngrok_client.open_tunnel(protocol, port, name)
        print tunnel
        return tunnel
