import sqlite3
import json
import random
import util
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

def removeTriggerResponseLinkForCase(caseID, triggerID, responseID):
	result = query_db("SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID))
	commit_db('DELETE FROM dtr_links WHERE diagnosis_id=? AND tr_link_id=?', ("1", result[0][0]))
	return ""

###
### CASE -> PATIENT
### management
###
def setCase(form):
	# load the case from ID if available, else create one
	caseID = form['caseID']
	
	# edit the CC

	# edit the HPI
	# edit the ROS
	rosList = form['ros'].split('\n')
	for item in rosList:
		value, sx = item.split(' ', 1)
		print(value + " of " + sx)
	# edit the PE
	peList = form['pe'].split('\n')
	for item in peList:
		value, sign = item.split(' ', 1)
		print(value + " of " + sign)
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

	# Add trigger / response



def generatePatientFromCase(caseID):	
	case = util.getCase(caseID)
	patient = case.generateNewPatient()
	response = {"patientID":patient.patientID, "patientName":(patient.firstname + patient.lastname)}
	return response

###
### USER
### management
###
def generateRandomPatientForUser(userID):
	caseList = query_db("SELECT id FROM cases", ())
	newPatientID = generatePatientFromCase(random.choice(caseList))['patientID']
	# add the patient to the user's patient list
	commit_db("INSERT INTO user_patients (user_id, patient_id) VALUES (?,?)", (userID, newPatientID))
	return newPatientID

def userNote(userID, patientID, note):
	response = []
	result = query_db("SELECT user_notes_id FROM user_notes WHERE user_id=? AND patient_id=?", (userID, patientID))
	if len(result) > 0:
		commit_db('UPDATE user_notes SET note=? WHERE user_notes_id=?', (note, result[0][0]))
	else:
		commit_db('INSERT INTO user_notes (user_id, patient_id, note) VALUES (?,?,?)', (userID, patientID, note))
	response.append('Done')
	return json.dumps(response)

###
### PATIENT
### management
###
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
