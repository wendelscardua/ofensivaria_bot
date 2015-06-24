import re
import random
import requests

def split(text, splits=0):
    return re.split('\s|\xa0', text, splits)

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
    REGEX = re.compile("(.*)\sou\s(.*)\??", re.UNICODE)

    def can_respond(self, message):
        return True

    def respond(self, message):
        text = re.split('\s|\xa0', message['text'], 1)[-1]
        choices = self.REGEX.findall(text)[0]

        if random.randint(1, 100) < 10:
            answer = 'sim'
        else:
            answer = random.choice(choices).strip()

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

class GithubLatest(Command):

    SLASH_COMMAND = '/commits'

    def respond(self, message):
        url = 'https://api.github.com/repos/fernandotakai/ofensivaria_bot/commits'
        response = requests.get(url)
        json = response.json()
        answer = []

        for commit in json[0:5]:
            commit = commit['commit']
            answer.append("%s: %s" % (commit['committer']['name'], commit['message']))

        self._bot.send_message(message['chat']['id'], '\n'.join(answer))

class ArchiveUrl(Command):

    SLASH_COMMAND = '/archive'

    def respond(self, message):
        url = split(message['text'], 1)[-1]

        archive_api = 'http://archive.org/wayback/available'
        response = requests.get(archive_api, params=dict(url=url))

        json = response.json()

        if json['archived_snapshots']:
            answer = json['archived_snapshots']['closest']['url']
        else:
            answer = 'Click here to archive - https://archive.is/?run=1&url=%s' % url

        self._bot.send_message(message['chat']['id'], answer, None, True)

COMMANDS = [PowerOff, Ping, Title, EitherOr, Help, GithubLatest, ArchiveUrl]
