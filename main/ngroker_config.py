import ConfigParser
import os

class Ngroker_Config(object):

    exec_path = os.path.dirname(os.path.abspath(__file__))

    _config = ConfigParser.ConfigParser()
    _config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ngroker.ini"))

    ngrok_api_url = _config.get('ngrok','api_url')
    ngrok_auth_token = _config.get('ngrok','auth_token')

    telegram_bot_token = _config.get('telegram','bot_token')
