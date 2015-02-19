from ersim import app
from ersim import response
from ersim import login
from ersim import edit
from flask import request
from flask import render_template
from flask import flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user
from ersim import user
import json


@app.route('/')
@login_required
def indexRoute():
	return render_template("FCMain.html")

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

@app.route('/interview')
@login_required
def interviewRoute():
	return render_template('FCInterview.html')

@app.route('/response', methods=['GET', 'POST'])
def responseRoute():
	if request.method == 'POST':
		return response.generateResponse(request.form['patientID'], request.form['trigger'])
	else:
		return 'you failed to POST correctly!'

@app.route('/notewriter')
@login_required
def noteWriterRoute():
	return render_template('FCNoteWriter.html')

@app.route('/edit/note', methods=['POST'])
@login_required
def saveNoteRoute():
	return edit.userNote(current_user.uid, request.form['patientID'], request.form['note'])

@app.route('/assessment')
@login_required
def assessmentRoute():
	return render_template('FCAssessment.html')

@app.route('/getAssessment', methods=['POST'])
@login_required
def getAssessmentRoute():
	return response.getAssessment(current_user.uid, request.form['patientID'])

@app.route('/quiz')
@login_required
def quizRoute():
	return render_template('FCQuiz.html')

@app.route('/getQuiz')
@login_required
def getQuizRoute():
	return response.getQuiz(current_user.uid, request.form['patientID'])

@app.route('/knowledgebase')
@login_required
def knowledgebaseRoute():
	return render_template("FCKnowledgebase.html")

@app.route('/getKnowledge', methods=['POST'])
@login_required
def getKnowledgeRoute():
	return response.getKnowledge(request.form['patientID'])

@app.route('/test')
def testRoute():
	return render_template("index.html")


@app.route('/getDiagnosisList', methods=['GET', 'POST'])
def getDiagnosisListRoute():
	return response.getDiagnosisList()

@app.route('/getPatientListForDiagnosis', methods=['POST'])
def getPatientListForDiagnosisRoute():
	return response.getPatientListForDiagnosis(request.form['diagnosisID'])

@app.route('/getPatientsForCurrentUser', methods=['GET'])
def getPatientsForCurrentUserRoute():
	return response.getPatientsForUser(current_user.uid)

@app.route('/getPatientsForUser', methods=['POST'])
def getPatientsForUserRoute():
	return response.getPatientsForUser(request.form['userID'])

@app.route('/getPatientsBriefChart', methods=['POST'])
def getPatientsBriefChartRoute():
	return response.getPatientsBriefChart(request.form['patientID'])

@app.route('/user/getCurrentUserName', methods=['GET'])
def getCurrentUserNameRoute():
	return response.getCurrentUserName()

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

@app.route('/user/getName', methods=['POST'])
@login_required
def userGetNameRoute():
	user.getName()

@app.route('/edit/case', methods=['GET', 'POST'])
@login_required
def editCase():
	if request.method == 'GET':
		return render_template("edit_case.html")
	elif request.method == 'POST':
		return edit.setCase(request.form)

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

@app.route('/edit/removeResponseForTrigger', methods=['POST'])
@login_required
def removeResponseForTriggerRoute():
	return edit.removeResponseForTrigger(request.form['triggerID'], request.form['responseID'])

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
	return json.dumps(edit.generatePatientForDiagnosis(request.form['diagnosisID']))

@app.route('/edit/generateRandomPatientForUser', methods=['POST'])
def generateRandomPatientForUserRoute():
	return json.dumps(edit.generateRandomPatientForUser(current_user.uid))

@app.route('/edit/deletePatient', methods=['POST'])
def deletePatientRoute():
	return edit.deletePatient(request.form['patientID'])