from ersim import app
from ersim import response
from ersim import login
from flask import request
from flask import render_template
from flask import flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user
from ersim import user


@app.route('/')
def index():
	return 'Index.'

@app.route('/response', methods=['GET', 'POST'])
def responseRoute():
	if request.method == 'POST':
		triggerValue = request.form['trigger']
		return response.generateResponse(1, triggerValue)
	else:
		return 'you failed to POST correctly!'

@app.route('/play')
@login_required
def playRoute():
	return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def loginRoute():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		uid = login.validate_user(username, password)
		if uid:
			login_user(user.get(uid))
			flash("logged in successfully")
			return redirect(request.args.get("next") or url_for("index"))
	elif request.method == 'GET':
		return render_template("login.html")
	else:
		return "Sucker"

@app.route('/settings')
@login_required
def settings():
	return "Settings for: " + current_user.name + " (UID: " + current_user.uid + ")"

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/login')