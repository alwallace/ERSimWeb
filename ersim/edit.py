import sqlite3
import json
import random
from flask import g
from ersim import query_db, commit_db, lastid_db

###
### TRIGGER -*-> RESPONSE 
### management
###
def getTriggerList():
	result = query_db('SELECT id, trigger FROM triggers')
	response = []
	for row in result:
		response.append({"id":row[0], "trigger":row[1]})
	return json.dumps(response)

def getResponseList():
	result = query_db('SELECT id, response, media_id FROM responses')
	response = []
	for row in result:
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})
	return json.dumps(response)

def getResponseListForTrigger(triggerID):
	result = query_db('SELECT responses.id, response, media_id FROM responses, tr_links WHERE tr_links.trigger_id=? AND tr_links.response_id=responses.id', (triggerID,))
	response = []
	for row in result:
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})
	return json.dumps(response)

def addResponseForTrigger(triggerID, responseValue):
	result = query_db('SELECT id FROM responses WHERE response=?', (responseValue,))
	response = []
	if len(result) > 0:
		responseID = result[0][0]
		trLinkIDResult = query_db('SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?', (triggerID, responseID))
		if len(trLinkIDResult) == 0:	
			commit_db('INSERT OR IGNORE INTO tr_links (trigger_id, response_id) VALUES (?,?)', (triggerID, responseID))
			response.append({"id":responseID, "response":responseValue, "media_id":0})
		else:
			response.append({"id":-1})
	else:
		commit_db('INSERT OR IGNORE INTO responses (response, media_id) VALUES (?,?)', (responseValue, ''))
		responseID = lastid_db()
		commit_db('INSERT OR IGNORE INTO tr_links (trigger_id, response_id) VALUES (?,?)', (triggerID, responseID))
		response.append({"id":responseID, "response":responseValue, "media_id":0})
	return json.dumps(response)

def removeResponseForTrigger(triggerID, responseID):
	commit_db('DELETE FROM tr_links WHERE trigger_id=? and response_id=?', (triggerID, responseID))
	return ""

###
### CASE -*-> (Trigger -*-> Response) 
### management
###
def getResponseListForCaseTrigger(caseID, triggerID):
	result = query_db('SELECT responses.id, response, media_id FROM responses, case_tr_links, tr_links WHERE tr_links.trigger_id=? AND tr_links.response_id=responses.id AND case_tr_links.case_id=? AND case_tr_links.tr_link_id=tr_links.id', (triggerID, caseID))
	response = []
	for row in result:
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})
	return json.dumps(response)

def addTriggerReponseLinkForCase(caseID, triggerID, responseID):
	tempTRLinkID = query_db("SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID))[0][0]
	result = query_db("SELECT id FROM case_tr_links WHERE case_id=? AND tr_link_id=?", ("1", tempTRLinkID))
	response = []
	if len(result) == 0:
		commit_db('INSERT OR IGNORE INTO case_tr_links (case_id, tr_link_id) VALUES (?, ?)', ("1", tempTRLinkID))
		response.append(lastid_db())
	return json.dumps(response)

def addTriggerResponseForCase(caseID, trigger, response):
	tresult = query_db("SELECT trigger_id FROM triggers WHERE trigger=?", (trigger,))
	rresult = query_db("SELECT response_id FROM responses WHERE response=?", (response,))
	# if the trigger or response was not found in the db, then create it and get the ID
	triggerID = -1
	if tresult == None:
		commit_db("INSERT INTO triggers (trigger) VALUES (?)", (trigger,))
		triggerID = lastid_db()
	else:
		triggerID = tresult[0][0]
	responseID = -1
	if rresult == None:
		commit_db("INSERT INTO response (response) VALUES (?)", (response,))
		responseID = lastid_db()
	else:
		responseID = rresult[0][0]

	addTriggerReponseLinkForCase(caseID, triggerID, responseID)

def removeResponseForDiagnosis(triggerID, diagnosisID, responseID):
	result = query_db("SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID))
	commit_db('DELETE FROM dtr_links WHERE diagnosis_id=? AND tr_link_id=?', ("1", result[0][0]))

	return ""

def generatePatientForDiagnosis(diagnosisID):
	sex = random.choice(['male', 'female'])
	firstnameCount = query_db('SELECT COUNT(*) FROM first_names WHERE sex=?', (sex,), True)[0]
	firstnameRandomOffset = random.randint(0, firstnameCount-1)
	firstname = query_db('SELECT firstname FROM first_names WHERE sex=? LIMIT 1 OFFSET ' + str(firstnameRandomOffset), (sex,), True)[0]
	lastnameCount = query_db('SELECT COUNT(*) FROM last_names', (), True)[0]
	lastnameRandomOffset = random.randint(0, lastnameCount-1)
	lastname = query_db('SELECT lastname from last_names LIMIT 1 OFFSET ' + str(lastnameRandomOffset), (), True)[0]

	patientName = lastname + ', ' + firstname
	commit_db("INSERT INTO patients (diagnosis_id, name, sex) VALUES (?,?,?)", (diagnosisID, patientName, sex))
	patientID = lastid_db()

	result = query_db('SELECT id, trigger FROM triggers', ())

	for tempTriggerRow in result:
		result2 = query_db('SELECT tr_links.id FROM dtr_links, tr_links WHERE dtr_links.diagnosis_id=? AND dtr_links.tr_link_id=tr_links.id AND tr_links.trigger_id=?', (diagnosisID, tempTriggerRow[0]))

		if len(result2) > 0:
			tempTRLinkID = random.choice(result2)[0]
			commit_db('INSERT INTO ptr_links (patient_id, tr_link_id) VALUES (?, ?)', (patientID,tempTRLinkID))

	response = {"patientID":patientID, "patientName":patientName}
	return response

def generateRandomPatientForUser(userID):
	diagnosisList = query_db("SELECT id FROM diagnosis", ())
	result = generatePatientForDiagnosis(diagnosisList[random.randint(0, len(diagnosisList)-1)][0])
	# add the patient to the user's patient list
	commit_db("INSERT INTO user_patients (user_id, patient_id) VALUES (?,?)", (userID, result['patientID']))
	return result

def getResponsesForPatient(patientID):
	response = []
	result = query_db("SELECT triggers.id, trigger, responses.id, response, media_id FROM triggers, responses, tr_links, ptr_links WHERE ptr_links.patient_id=? AND ptr_links.tr_link_id=tr_links.id AND tr_links.trigger_id=triggers.id AND tr_links.response_id=responses.id", (patientID,))
	for row in result:
		response.append({"trigger_id":row[0], "trigger":row[1], "response_id":row[2], "response":row[3], "media_id":row[4]})
	return json.dumps(response)

def deletePatient(patientID):
	response = []
	commit_db('DELETE FROM ptr_links WHERE patient_id=?', (patientID,))
	commit_db('DELETE FROM patients WHERE patient_id=?', (patientID,))
	response.append('Done')
	return json.dumps(response)

def userNote(userID, patientID, note):
	response = []
	result = query_db("SELECT user_notes_id FROM user_notes WHERE user_id=? AND patient_id=?", (userID, patientID))
	if len(result) > 0:
		commit_db('UPDATE user_notes SET note=? WHERE user_notes_id=?', (note, result[0][0]))
	else:
		commit_db('INSERT INTO user_notes (user_id, patient_id, note) VALUES (?,?,?)', (userID, patientID, note))
	response.append('Done')
	return json.dumps(response)

def setCase(form):
	# load the case from ID if available, else create one
	caseID = form['caseID']
	if caseID == -1:
		commit_db("INSERT INTO cases (case_id) VALUES (NULL)", ())
		caseID = lastid_db()

	# get the trigger list and make a dictionary
	tlist = getTriggerList()
	triggerToID = {}
	for item in tlist:
		triggerToID[item['trigger']] = item['id']

	# edit the CC
	addTriggerResponseForCase(caseID, "cc", form['cc'])

	# edit the HPI
	addTriggerResponseForCase(caseID, "hpi", form['hpi'])

	# edit the ROS
	rosList = form['ros'].split('\n')
	for item in rosList:
		value, sx = item.split(' ', 1)
		addTriggerResponseForCase(caseID, sx, value)

	# edit the PE
	peList = form['pe'].split('\n')
	for item in peList:
		value, sign = item.split(' ', 1)
		addTriggerResponseForCase(caseID, sign, value)

	# edit the labs
	labList = form['labs'].split('\n')
	for item in labList:
		print("lab item " + item)

	# edit the imaging
	imageList = form['imaging'].split('\n')
	for item in imageList:
		print("image item " + item)

	# edit the ddx
	ddxList = form['ddx'].split('\n')
	for item in ddxList:
		print("ddx item " + item)

	# edit the orders
	orderList = form['orders'].split('\n')
	for item in orderList:
		print("order item " + item)

	# edit the interventions
	interventionList = form['interventions'].split('\n')
	for item in interventionList:
		print("intervention item " + item)

