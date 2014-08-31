import sqlite3
import json
import random
from flask import g
from ersim import query_db, commit_db, lastid_db

def getTriggerList():
	result = query_db('SELECT id, trigger FROM triggers')

	response = []
	for row in result:
		response.append({"id":row[0], "trigger":row[1]})

	return json.dumps(response)

def getResponseListFor(triggerID):
	result = query_db('SELECT responses.id, response, media_id FROM responses, tr_links WHERE tr_links.trigger_id=? AND tr_links.response_id=responses.id', (triggerID,))

	response = []
	for row in result:
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})

	return json.dumps(response)

def getResponseListForDiagnosis(triggerID, diagnosisID):
	result = query_db('SELECT responses.id, response, media_id FROM responses, dtr_links, tr_links WHERE tr_links.trigger_id=? AND tr_links.response_id=responses.id AND dtr_links.diagnosis_id=? AND dtr_links.tr_link_id=tr_links.id', (triggerID, diagnosisID))

	response = []
	for row in result:
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})
		
	return json.dumps(response)

def addResponseForTrigger(triggerID, responseValue):
	result = query_db('SELECT id FROM responses WHERE response=?', (responseValue,))
	response = []
	if len(result) > 0:
		responseID = result[0][0]
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



def addResponseForDiagnosis(triggerID, diagnosisID, responseID):
	result = query_db("SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID))
	result2 = query_db("SELECT id FROM dtr_links WHERE diagnosis_id=? AND tr_link_id=?", ("1", result[0][0]))
	response = []

	if len(result2) == 0:
		commit_db('INSERT OR IGNORE INTO dtr_links (diagnosis_id, tr_link_id) VALUES (?, ?)', ("1", result[0][0]))

		result = query_db("SELECT id, response, media_id FROM responses WHERE id=?", (responseID,))
		row = result[0]
		response.append({"id":row[0], "response":row[1], "media_id":row[2]})

	return json.dumps(response)

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

	response = [{"patientID":patientID}]
	return json.dumps(response)

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
