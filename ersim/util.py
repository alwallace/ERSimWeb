import sqlite3
import json
import random
from flask import g
from ersim import query_db, commit_db, lastid_db

class Patient:
	def __init__(self, patientID, first, last, sex):
		self.patientID = patientID
		self.first = first
		self.last = last
		self.sex = sex

class Trigger:
	def __init__(self, triggerID, trigger):
		self.triggerID = triggerID
		self.trigger = trigger

class Response:
	def __init__(self, responseID, response, responseMedia):
		self.responseID = responseID
		self.response = response
		self.responseMedia = responseMedia

class Action:
	def __init__(self, actionID, action):
		self.actionID = actionID
		self.action = action

# NOTE: 
# triggerResponseList = [{trigger:<Trigger>, responses:[<Response>, ]}]
# goalTriggers = [<Trigger>, ]
# goalActions = [<Action>, ]
class Case:
	def __init__(self, caseID, triggerResponseList, goalTriggers, goalActions):
		self.caseID = caseID
		self.triggerResponseList = triggerResponseList
		self.goalTriggers = goalTriggers
		self.goalActions = goalActions

	def generateNewPatient():
		# Select the sex
		sex = random.choice(['male', 'female'])
		# Select a first name, then last name
		firstnameCount = query_db('SELECT COUNT(*) FROM first_names WHERE sex=?', (sex,), True)[0]
		firstnameRandomOffset = random.randint(0, firstnameCount-1)
		firstname = query_db('SELECT firstname FROM first_names WHERE sex=? LIMIT 1 OFFSET ' + str(firstnameRandomOffset), (sex,), True)[0]
		lastnameCount = query_db('SELECT COUNT(*) FROM last_names', (), True)[0]
		lastnameRandomOffset = random.randint(0, lastnameCount-1)
		lastname = query_db('SELECT lastname from last_names LIMIT 1 OFFSET ' + str(lastnameRandomOffset), (), True)[0]

		patientName = lastname + ', ' + firstname
		# Create the Patient: 
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

class User:
	def __init__(self, userID, username, password):
		self.userID = userID
		self.username = username
		self.password = password