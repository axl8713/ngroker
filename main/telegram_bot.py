import ngroker
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telepot.loop import MessageLoop
import time
from ngroker_config import Ngroker_Config
import logging
import os

logger = logging.getLogger(__name__)

class Telegram_bot(object):

    _bot_command_start = "/start"
    _bot_command_open_tunnel = "/open_tunnel"
    _bot_command_new_tunnel = "/new_tunnel"
    _bot_command_stop = '/stop'

    _callback_data_ssh = 'ssh'
    _callback_data_manager = 'manager'
    _callback_data_deluge = 'deluge'
    _callback_data_tcp = 'tcp'
    _callback_data_http = 'http'

    _predefined_manager_tunnel_data = {"protocol":'http', "port": 4040, "name": "ngrok manager"}
    _predefined_ssh_tunnel_data = {"protocol": "tcp", "port": 22, "name": "SSH"}
    _predefined_deluge_webui_data = {"protocol": "http", "port": 8113, "name": "deluge webui"}

    _predefined_tunnels = {
        _callback_data_ssh: _predefined_ssh_tunnel_data,
        _callback_data_manager: _predefined_manager_tunnel_data,
        _callback_data_deluge: _predefined_deluge_webui_data
    }

    def __init__(self):

       self._bot = telepot.Bot(Ngroker_Config.telegram_bot_token)
       MessageLoop(self._bot, {'chat': self.handle_message, 'callback_query': self.on_callback_query}).run_as_thread()

       self._ngrok_client = ngroker.Ngroker()
       self._ngrok_client.start()

    def handle_message(self, message):

        content_type, chat_type, chat_id = telepot.glance(message)

        print message

        try:
            self._check_recipient(message['from']['id'])

            if content_type == 'text':

                command = message['text'];

                logger.debug("%s command received", command)

                # TODO: replace with dictionary mapping
                if command == self._bot_command_start:
                    self.handle_start_command(chat_id)

                elif command == self._bot_command_open_tunnel:
                    self.handle_open_tunnel_command(chat_id)

                elif command == self._bot_command_new_tunnel:
                    self.handle_new_tunnel_command(chat_id)

                elif command == self._bot_command_stop:
                    self.handle_stop_command(chat_id)
                else:
                    raise Exception("command not recognized")

        except Exception as ex:
            logger.error("error in handling message: " + str(ex))
            self._bot.sendMessage(chat_id, "someting went wrong: " + str(ex))

    def _check_recipient(self, recipient_id):
        if str(recipient_id) != Ngroker_Config.telegram_allowed_recipient_id:
            raise Exception("access denied.")
        else:
            pass

    def handle_start_command(self, chat_id):
        self._ngrok_client.start()
        keyboard = ReplyKeyboardMarkup(keyboard=[
                         [self._bot_command_open_tunnel, self._bot_command_new_tunnel],
                         [self._bot_command_stop]
        ])
        self._bot.sendMessage(chat_id, 'Select a command', reply_markup=keyboard)

    def handle_open_tunnel_command(self, chat_id):
        if self._ngrok_client.is_ngrok_started:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    # TODO: to be created from predefined_tunnels
                    InlineKeyboardButton(text=self._predefined_ssh_tunnel_data["name"], callback_data=self._callback_data_ssh),
                    InlineKeyboardButton(text=self._predefined_manager_tunnel_data["name"], callback_data=self._callback_data_manager),
                    InlineKeyboardButton(text=self._predefined_deluge_webui_data["name"], callback_data=self._callback_data_deluge)
                ],
            ])
            self._bot.sendMessage(chat_id, 'Please select the tunnel to be opened.', reply_markup=keyboard)
        else:
            self.send_please_start_ngrok_message(chat_id)

    def send_please_start_ngrok_message(self, chat_id):
        self._bot.sendMessage(chat_id, 'Please start client first via ' + self._bot_command_start + ' command.')

    def handle_new_tunnel_command(self, chat_id):
        if self._ngrok_client.is_ngrok_started:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='TCP', callback_data=self._callback_data_tcp),
                    InlineKeyboardButton(text='HTTP', callback_data=self._callback_data_http),
                ],
            ])
            self._bot.sendMessage(chat_id, 'Please select a protocol for the tunnel.', reply_markup=keyboard)
        else:
            self.send_please_start_ngrok_message(chat_id)

    def handle_stop_command(self, chat_id):
        self._ngrok_client.stop()
        keyboard = ReplyKeyboardMarkup(keyboard=[
                         [self._bot_command_start],
        ])
        self._bot.sendMessage(chat_id, 'Select ' + self._bot_command_start + ' command to start client', reply_markup=keyboard)

    def on_callback_query(self, message):
        query_id, from_id, query_data = telepot.glance(message, flavor='callback_query')

        try:
            self._check_recipient(from_id)
            self.open_predefined_tunnel(self._predefined_tunnels[query_data], query_id, from_id)
        except Exception as ex:
            logger.error("error in handling query: " + str(ex))
            self._bot.sendMessage(from_id, "someting went wrong: " + str(ex))


    def open_predefined_tunnel(self, tunnel_data, query_id, from_id):
        self._bot.answerCallbackQuery(query_id, text='Opening ' + tunnel_data["name"] + ' tunnel. Stay tight.')
        tunnel = self._ngrok_client.open_tunnel(tunnel_data["protocol"], tunnel_data["port"], tunnel_data["name"])
        self._bot.sendMessage(from_id, str(tunnel))
