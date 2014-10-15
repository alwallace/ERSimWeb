import sqlite3
import json
from flask import g
from flask.ext.login import current_user
from ersim import query_db, commit_db

def generateResponse(patientID, triggerValue):
	triggerValue = triggerValue.lower()
	responseText = "** Please ask a question (history, physical exam, etc.) with '?' [ex: 'pain?' will ask the patient if they have pain] or perform an action (medications, lab, imaging, etc.) with '.' [ex: '.cbc' will place an order for a CBC] **"

	responseMedia = ""

	# if its a request for response (ends with ?)
	if triggerValue.endswith('?'):
		result = query_db('SELECT response, media_id, tr_links.trigger_id FROM responses, tr_links, ptr_links, triggers WHERE responses.id=tr_links.response_id AND tr_links.id=ptr_links.tr_link_id AND ptr_links.patient_id=? AND tr_links.trigger_id=triggers.id AND triggers.trigger=?', (patientID, triggerValue[:-1]), True)

		if result is None:
			responseText = "I do not want to answer that."
		else:
			responseText = result[0]
			# Record the user trigger
			commit_db("INSERT INTO user_triggers (user_id, patient_id, trigger_id) VALUES (?,?,?)", (current_user.uid, patientID, result[2]))
			result = query_db('SELECT file FROM media WHERE media.id=?', (result[1],), True)
			if result is not None:
				responseMedia = result[0]

	# if its a request to perform an action (starts with .)
	elif triggerValue.startswith('.'):
		# check if it is a valid action
		tempActionID = query_db('SELECT id FROM actions WHERE name=?', (triggerValue[1:],), True)
		if tempActionID is not None:
			tempActionID = tempActionID[0]

			# check to see if the user already did the action so we don't do it again
			tempUserAction = query_db('SELECT user_action_id FROM user_actions WHERE user_id=? AND action_id=? and patient_id=?', (1, tempActionID, patientID), True)
			if tempUserAction is None:
				commit_db('INSERT INTO user_actions (user_id, action_id, patient_id) VALUES (?,?,?)', (1, tempActionID, patientID))
				responseText = "* Done. *"
			else:
				responseText = "* You already did that! *"
		else:
			responseText = "* Could not perform that action, not available. *"

	response = {"text":responseText, "media":responseMedia}

	return json.dumps(response)

def getAssessment(userID, patientID):
	response = []
	# Get all the goal triggers
	resultGoalTriggers = query_db("SELECT trigger.id, trigger.trigger FROM patients, triggers, goal_triggers WHERE patient_id=? AND patients.diagnosis_id=goal_triggers.diagnosis_id AND triggers.id=goal_triggers.trigger_id" (patientID,))
	# Get all the user triggers
	resultUserTriggers = query_db("SELECT trigger.id, trigger.trigger FROM triggers, user_triggers WHERE triggers.id=trigger_id AND user_id=? AND patient_id=?", (userID, patientID))

	# Get the missed goal triggers
	# Get the matched goal triggers
	# Get the unnecessary user triggers
	missedTriggers = []
	matchedTriggers = []
	unnecessaryTriggers = []
	for row in resultUserTriggers:
		if row in resultGoalTriggers:
			matchedTriggers.append(row)
		else:
			unnecessaryTriggers.append(row)
		resultGoalTriggers.remove(row)
	missedTriggers = resultGoalTriggers
	response.append({"missed":missedTriggers, "matched":matchedTriggers, "unnecessary":unnecessaryTriggers})
	return json.dumps(response)

def getDiagnosisList():
	response = []
	results = query_db("SELECT id, name FROM diagnosis", ())
	for row in results:
		response.append({"id":row[0], "name":row[1]})
	return json.dumps(response)

def getPatientListForDiagnosis(diagnosisID):
	response = []
	results = query_db("SELECT patient_id, name FROM patients WHERE diagnosis_id=?", (diagnosisID,))
	for row in results:
		response.append({"id":row[0], "name":row[1]})
	return json.dumps(response)

def getPatientsForUser(userID):
	response = []
	results = query_db("SELECT patients.patient_id, name, sex FROM patients, user_patients WHERE user_patients.user_id=? AND user_patients.user_patient_id=patients.patient_id", (userID,))
	for row in results:
		response.append({"patient_id":row[0], "patient_name":row[1], "patient_sex":row[2]})
	return json.dumps(response)

def getPatientsBriefChart(patientID):
	response = []
	result = query_db('SELECT response, media_id FROM responses, tr_links, ptr_links, triggers WHERE responses.id=tr_links.response_id AND tr_links.id=ptr_links.tr_link_id AND ptr_links.patient_id=? AND tr_links.trigger_id=triggers.id AND triggers.trigger="cc"', (patientID,), True)
	response.append({"cc":result[0]})
	return json.dumps(response)

def getCurrentUserName():
	response = []
	response.append({"user_name":current_user.name})
	return json.dumps(response)

