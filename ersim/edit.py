import sqlite3
import json
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