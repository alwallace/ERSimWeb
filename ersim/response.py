import sqlite3

def generateResponse(patientID, triggerValue):
	conn = sqlite3.connect('extra/test.sqlite')
	c = conn.cursor()
	c.execute('SELECT response FROM responses, tr_links, ptr_links, triggers WHERE responses.id=tr_links.response_id AND tr_links.id=ptr_links.tr_link_id AND ptr_links.patient_id=? AND tr_links.trigger_id=triggers.id AND triggers.trigger=?', (patientID, triggerValue))
	response = c.fetchone()
	
	if response == None:
		response = "I dont' want to answer that."
	else:
		response = response[0]

	conn.close()
	return response


