from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Result

@app.route('/')
def index():
	return "Hello Becky!"


@app.route('/<name>')
def hello(name):
	return "Hello {}!".format(name)


if __name__ == '__main__':
	app.run()