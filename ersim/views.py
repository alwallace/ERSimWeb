from ersim import app
from ersim import response
from ersim import login
from ersim import edit
from flask import request
from flask import render_template
from flask import flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user
from ersim import user

@app.route('/')
@login_required
def indexRoute():
	return render_template("FCMain.html")

@app.route('/play')
@login_required
def playRoute():
	return render_template('main.html')

@app.route('/response', methods=['GET', 'POST'])
def responseRoute():
	if request.method == 'POST':
		patientID = request.form['patientID']
		triggerValue = request.form['trigger']
		return response.generateResponse(patientID, triggerValue)
	else:
		return 'you failed to POST correctly!'

@app.route('/getDiagnosisList', methods=['GET', 'POST'])
def getDiagnosisListRoute():
	return response.getDiagnosisList()

@app.route('/getPatientListForDiagnosis', methods=['POST'])
def getPatientListForDiagnosisRoute():
	return response.getPatientListForDiagnosis(request.form['diagnosisID'])

@app.route('/login', methods=['GET', 'POST'])
def loginRoute():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		uid = login.validate_user(username, password)
		if uid:
			login_user(user.get(uid))
			flash("logged in successfully")
			return redirect(request.args.get("next") or url_for("indexRoute"))
	elif request.method == 'GET':
		return render_template("FPIndex.html")
	else:
		return "Sucker"

@app.route('/settings')
@login_required
def settingsRoute():
	return "Settings for: " + current_user.name + " (UID: " + current_user.uid + ")"

@app.route('/edit')
@login_required
def editRoute():
	return render_template("edit_responses.html")

@app.route('/logout')
@login_required
def logoutRoute():
	logout_user()
	return redirect('/login')

@app.route('/edit/getTriggerList')
@login_required
def getTriggerListRoute():
	return edit.getTriggerList()

@app.route('/edit/getResponseListFor', methods=['POST'])
@login_required
def getResponseListForRoute():
	return edit.getResponseListFor(request.form['triggerID'])

@app.route('/edit/getResponseListForDiagnosis', methods=['POST'])
@login_required
def getResponseListForDiagnosisRoute():
	return edit.getResponseListForDiagnosis(request.form['triggerID'], request.form['diagnosisID'])

@app.route('/edit/addResponseForDiagnosis', methods=['POST'])
@login_required
def addResponseForDiagnosis():
	return edit.addResponseForDiagnosis(request.form['triggerID'], request.form['diagnosisID'], request.form['responseID'])

@app.route('/edit/removeResponseForDiagnosis', methods=['POST'])
@login_required
def removeResponseForDiagnosis():
	return edit.removeResponseForDiagnosis(request.form['triggerID'], request.form['diagnosisID'], request.form['responseID'])

@app.route('/edit/addResponseForTrigger', methods=['POST'])
@login_required
def addResponseForTrigger():
	return edit.addResponseForTrigger(request.form['triggerID'], request.form['responseValue'])

@app.route('/edit/getResponsesForPatient', methods=['POST'])
@login_required
def getResponsesForPatientRoute():
	return edit.getResponsesForPatient(request.form['patientID'])

@app.route('/view/patient', methods=['GET'])
@login_required
def viewPatientRoute():
	return render_template("viewPatient.html")

@app.route('/edit/generatePatientForDiagnosis', methods=['POST'])
def generatePatientForDiagnosisRoute():
	return edit.generatePatientForDiagnosis(request.form['diagnosisID'])

@app.route('/edit/deletePatient', methods=['POST'])
def deletePatientRoute():
	return edit.deletePatient(request.form['patientID'])

@app.route('/test')
def testRoute():
	return render_template("index.html")