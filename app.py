import sys
import logging

from flask import Flask
from flask import request

from bot import TelegramBot

app = Flask(__name__)
app.config.from_envvar("CONFIG_FILE")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

bot = TelegramBot(app.config['TOKEN'])

logger.propagate = False

app.route('/bot-webhook')
def webhook():
    update = request.get_json()
    bot.process_update(update)
    return dict(status='ok')

if __name__ == '__main__':
    me = bot.me()
    logger.info("Bot named %(first_name)s/%(username)s" % me['result'])
    app.logger.addHandler(handler)
    app.run(host="0.0.0.0")
