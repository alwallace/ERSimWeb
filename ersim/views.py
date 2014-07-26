from ersim import app
from ersim import response
from flask import request
from flask import render_template


@app.route('/')
def index():
	return 'Index.'

@app.route('/response', methods=['GET', 'POST'])
def responseFunc():
	if request.method == 'POST':
		triggerValue = request.form['trigger']
		return response.generateResponse(1, triggerValue)
	else:
		return 'you failed to POST correctly!'

@app.route('/play')
def play():
	return render_template('main.html')
