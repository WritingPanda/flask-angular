from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn
import json
import operator
import os
import requests
import re
import nltk

#################
# configuration #
#################

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

q = Queue(connection=conn)

from models import *

##########
# helper #
##########

def count_and_save_words(url):
	errors = []

	try:
		r = requests.get(url)
	except:
		errors.append(
			"Unable to get URL. Please make sure it is valid and try again."
		)
		return {"error": errors}
	
	# text processing
	raw = BeautifulSoup(r.text).get_text()
	nltk.data.path.append('./nltk_data/') # set the path
	tokens = nltk.word_tokenize(raw)
	text = nltk.Text(tokens)

	# remove punctuation, count raw words
	nonPunct = re.compile('.*[A-Za-z].*')
	raw_words = [w for w in text if nonPunct.match(w)]
	raw_word_count = Counter(raw_words)

	# stop words
	no_stop_words = [w for w in raw_words if w.lower() not in stops]
	no_stop_words_count = Counter(no_stop_words)

	# save the results
	try:
		result=Result(
			url=url,
			result_all=raw_word_count,
			result_no_stop_words=no_stop_words_count
		)
		db.session.add(result)
		db.session.commit()
		return result.id
	except:
		errors.append("Unable to add item to database.")
		return {"error": errors}


##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
	results = {}
	if request.method == "POST":
		# get the URL the user has entered
		url = request.form['url']
		if 'http://' not in url[:7]:
			url = 'http://' + url
		job = q.enqueue_call(
			func=count_and_save_words, args=(url,), result_ttl=5000
		)
		print(job.get_id())
	return render_template(
		'index.html',
		results=results
	)


@app.route("/start", methods=["POST"])
def get_counts():
	# get url
	data = json.loads(request.data.decode())
	url = data['url']
	# form URL, id necessary
	if 'http://' not in url[:7]:
		url = 'http://' + url
	# start job
	job = q.enqueue_call(
		func=count_and_save_words, args=(url,), result_ttl=5000
	)
	return job.get_id()


@app.route("/results/<job_key>", methods=["GET"])
def get_results(job_key):
	job = Job.fetch(job_key, connection=conn)

	if job.is_finished:
		result = Result.query.filter_by(id=job.result).first()
		results = sorted(
			result.result_no_stop_words.items(),
			key=operator.itemgetter(1),
			reverse=True
		)[:10]
		return jsonify(results)
	else:
		return "Job has not finished.", 202


if __name__ == '__main__':
	app.run()