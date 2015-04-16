from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
	return "Hello Becky!"


@app.route('/<name>')
def hello(name):
	return "Hello {}!".format(name)


if __name__ == '__main__':
	app.run()