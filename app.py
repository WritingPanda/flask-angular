from flask import Flask
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/')
def index():
	return "Hello Becky!"


@app.route('/<name>')
def hello(name):
	return "Hello {}!".format(name)


if __name__ == '__main__':
	print(os.environ['APP_SETTINGS'])
	app.run()