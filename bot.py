import re
import redis
import random
import requests

class Command(object):

    SLASH_COMMAND = None

    def __init__(self, bot, redis):
        self._bot = bot
        self._redis = redis

    def can_respond(self, message):
        if self.SLASH_COMMAND:
            return message['text'].startswith(self.SLASH_COMMAND)

        return False

    def process(self, bot, message):
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
    regex = re.compile("([\s\w]+)\sou\s([\s\w]+)\??", re.UNICODE)

    def can_respond(self, message):
        text = message['text']
        return '@ofensivaria_bot' in text and bool(self.regex.search(message['text']))

    def respond(self, message):
        text = re.split('\s|\xa0', message['text'], 1)[-1]
        choices = self.regex.findall(text)[0]

        if random.randint(1, 100) < 10:
            answer = 'sim'
        else:
            answer = random.choice(choices)

        self._bot.send_message(message['chat']['id'], answer, message.get('message_id', None))

class PowerOff(Command):

    SLASH_COMMAND = '/staph'

    def can_respond(self, message):
        self._bot.stop()

class Help(Command):

    SLASH_COMMAND = '/help'

    def respond(self, message):
        answer = 'Deus ajuda quem cedo madruga'
        self._bot.send_message(message['chat']['id'], answer, message.get('message_id', None))

class TelegramBot(object):

    COMMANDS = [PowerOff, Ping, Title
                EitherOr, Help]

    def __init__(self, token):
        self.__running = True
        self._pool_sleep_time = 5
        self._redis = redis.Redis()
        self._token = token
        self._url = 'https://api.telegram.org/bot%s' % self._token
        
        self._processed_status = set(map(int, self._redis.smembers('bot:updates')))

        self._commands = [cls(self, self._redis) for cls in self.COMMANDS]

    def _send_request(self, method, data=None, is_post=False):
        url = "%s/%s" % (self._url, method)

        print 'Sending request to %s using params %s' % (url, data)

        if is_post:
            response = requests.post(url, data=data)
        else:
            response = requests.get(url, params=data)

        return response.json()

    def process_update(self, update):
        if update['update_id'] in self._processed_status:
            return
        
        self._redis.sadd('bot:updates', update['update_id'])
        self._processed_status.add(update['update_id'])

        if 'message' not in update:
            return

        message = update['message']
        
        for command in self._commands:
            try:
                command.process(self, message)
            except Exception, e:
                print 'Error processing %s %s' % (command, e)

    def get_updates(self):
        data = dict(offset=max(self._processed_status) + 1) if self._processed_status else None
        return self._send_request('getUpdates', data=data).get('result', [])

    def send_message(self, chat_id, message, in_reply_to=None):
        data = dict(chat_id=chat_id, text=message)

        if in_reply_to:
            data['reply_to_message_id'] = int(in_reply_to)

        return self._send_request('sendMessage', data, is_post=True)

    def start_pool(self):
        while self.__running:

            print 'getting updates'
            updates = bot.get_updates()

            print 'got %s' % updates

            for update in updates:
                print "Processing %s" % update
                bot.process_update(update)

            print 'waiting %ss' % self._pool_sleep_time
            time.sleep(self._pool_sleep_time)

    def stop(self):
        self.__running = False

if __name__ == '__main__':
    import sys
    import time

    bot = TelegramBot(sys.argv[1])

    bot.start_pool()
