import sqlite3

def generateResponse(patientID, triggerValue):
	response = "** Please ask a question (history, physical exam, etc.) with '?' [ex: 'pain?' will ask the patient if they have pain] or perform an action (medications, lab, imaging, etc.) with '.' [ex: '.cbc' will place an order for a CBC] **"
	# if its a request for response (ends with ?)
	if triggerValue.endswith('?'):
		conn = sqlite3.connect('extra/test.sqlite')
		c = conn.cursor()
		c.execute('SELECT response FROM responses, tr_links, ptr_links, triggers WHERE responses.id=tr_links.response_id AND tr_links.id=ptr_links.tr_link_id AND ptr_links.patient_id=? AND tr_links.trigger_id=triggers.id AND triggers.trigger=?', (patientID, triggerValue[:-1]))
		response = c.fetchone()

		if response == None:
			response = "I do not want to answer that."
		else:
			response = response[0]

		conn.close()

	# if its a request to perform an action (starts with .)
	elif triggerValue.startswith('.'):
		conn = sqlite3.connect('extra/test.sqlite')
		c = conn.cursor()

		# Check to see if that is a valid action
		c.execute('SELECT id FROM actions WHERE name=?', (triggerValue[1:],))
		tempActionID = c.fetchone()
		if tempActionID != None:
			tempActionID = tempActionID[0]

			# check to see if the user already did the action so we don't do it again
			c.execute('SELECT user_action_id FROM user_actions WHERE user_id=? AND action_id=? and patient_id=?', (1, tempActionID, 1))
			tempUserAction = c.fetchone()
			if tempUserAction == None:
				c.execute('INSERT INTO user_actions (user_id, action_id, patient_id, timestamp) VALUES (?,?,?,CURRENT_TIMESTAMP)', (1, tempActionID, 1))
				conn.commit()
				response = "* Done. *"
			else:
				response = "* You already did that! *"
		else:
			response = "* Could not perform that action, not available. *"

		conn.close()

	return response