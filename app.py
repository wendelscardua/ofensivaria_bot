from flask import Flask

app = Flask(__name__)

app.route('/bot-webhook')
def webhook():
    print 'webhookmemaybe'

if __name__ == '__main__':
    app.run(host="0.0.0.0")
