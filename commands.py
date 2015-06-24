class Command(object):
    def process(self, bot, message):
        if self.can_respond(message):
            self.respond(bot, message)

class Ping(Command):
    def can_respond(self, message):
        return message == 'ping'

    def respond(self, bot, message):
        print self.send_message(message['chat']['id'], 'ping')

class BotCommands(object):
    COMMANDS = [Ping]
    
    def __init__(self):
        self.__commands = [cls() for cls in self.COMMANDS]

    def register(cls, command):
        self.COMMANDS.append(command)
