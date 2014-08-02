import sqlite3
import json
from flask import g
from ersim import query_db, commit_db

def generateResponse(patientID, triggerValue):
	responseText = "** Please ask a question (history, physical exam, etc.) with '?' [ex: 'pain?' will ask the patient if they have pain] or perform an action (medications, lab, imaging, etc.) with '.' [ex: '.cbc' will place an order for a CBC] **"

	responseMedia = ""

	# if its a request for response (ends with ?)
	if triggerValue.endswith('?'):
		result = query_db('SELECT response, media_id FROM responses, tr_links, ptr_links, triggers WHERE responses.id=tr_links.response_id AND tr_links.id=ptr_links.tr_link_id AND ptr_links.patient_id=? AND tr_links.trigger_id=triggers.id AND triggers.trigger=?', (patientID, triggerValue[:-1]), True)

		if result is None:
			responseText = "I do not want to answer that."
		else:
			responseText = result[0]

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
			tempUserAction = query_db('SELECT user_action_id FROM user_actions WHERE user_id=? AND action_id=? and patient_id=?', (1, tempActionID, 1), True)
			if tempUserAction is None:
				commit_db('INSERT INTO user_actions (user_id, action_id, patient_id, timestamp) VALUES (?,?,?,CURRENT_TIMESTAMP)', (1, tempActionID, 1))
				responseText = "* Done. *"
			else:
				responseText = "* You already did that! *"
		else:
			responseText = "* Could not perform that action, not available. *"

	response = {"text":responseText, "media":responseMedia}

	return json.dumps(response)