import sqlite3
import json
import random
from flask import g
from ersim import query_db, commit_db

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

def generatePatient(diagnosisID):
	patientName = "Stupid Name " + str(random.random())
	commit_db("INSERT INTO patients (diagnosis_id, name) VALUES (?,?)", (diagnosisID, patientName))
	patientID = query_db("SELECT last_insert_rowid()", (), True)[0]

	result = query_db('SELECT id, trigger FROM triggers', ())

	for tempTriggerRow in result:
		result2 = query_db('SELECT tr_links.id FROM dtr_links, tr_links WHERE dtr_links.diagnosis_id=? AND dtr_links.tr_link_id=tr_links.id AND tr_links.trigger_id=?', (diagnosisID, tempTriggerRow[0]))

		if len(result2) > 0:
			tempTRLinkID = random.choice(result2)[0]
			commit_db('INSERT INTO ptr_links (patient_id, tr_link_id) VALUES (?, ?)', (patientID,tempTRLinkID))

	response = [{"patientID":patientID}]
	return json.dumps(response)