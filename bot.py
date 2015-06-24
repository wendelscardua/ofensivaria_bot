import re
import redis
import random
import requests

class Command(object):

    def __init__(self, bot, redis):
        self._bot = bot
        self._redis = redis

    def can_respond(self, message):
        return True

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

class TelegramBot(object):

    COMMANDS = [Ping, Title, EitherOr]

    def __init__(self, token):
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

if __name__ == '__main__':
    import sys
    import time

    bot = TelegramBot(sys.argv[1])

    while True:
        print 'getting updates'
        updates = bot.get_updates()

        print 'got %s' % updates

        for update in updates:
            print "Processing %s" % update
            bot.process_update(update)

        print 'waiting 5s'
        time.sleep(5)
