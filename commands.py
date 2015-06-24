import re
import random

class Command(object):

    SLASH_COMMAND = None
    REPLY_NEEDED = False
    REGEX = None

    def __init__(self, bot, redis):
        self._bot = bot
        self._redis = redis

    def can_respond(self, message):
        if self.SLASH_COMMAND:
            return message['text'].startswith(self.SLASH_COMMAND)

        return False

    def process(self, bot, message):
        text = message['text']

        if self.REPLY_NEEDED and not text.startswith('@ofensivaria_bot'):
            return

        if self.REGEX and not self.REGEX.search(message['text']):
            return

        if self.can_respond(message):
            self.respond(message)

class Ping(Command):
    def can_respond(self, message):
        return message['text'] == 'ping'

    def respond(self, message):
        self._bot.send_message(message['chat']['id'], 'pong')

class Title(Command):
    def can_respond(self, message):
        return message['text'] == u'/title'
    
    def respond(self, message):
        self._bot.send_message(message['chat']['id'], 'http://imgur.com/a/0OlQR')

class EitherOr(Command):
    REPLY_NEEDED = True
    REGEX = re.compile("([\s\w]+)\sou\s([\s\w]+)\??", re.UNICODE)

    def can_respond(self, message):
        return True

    def respond(self, message):
        text = re.split('\s|\xa0', message['text'], 1)[-1]
        choices = self.REGEX.findall(text)[0]

        if random.randint(1, 100) < 10:
            answer = 'sim'
        else:
            answer = random.choice(choices)

        self._bot.send_message(message['chat']['id'], answer, message.get('message_id', None))

class PowerOff(Command):

    SLASH_COMMAND = '/staph'

    def respond(self, message):
        self._bot.stop()

class Help(Command):

    SLASH_COMMAND = '/help'

    def respond(self, message):
        answer = 'Deus ajuda quem cedo madruga'
        self._bot.send_message(message['chat']['id'], answer, message.get('message_id', None))

COMMANDS = [PowerOff, Ping, Title, EitherOr, Help]
