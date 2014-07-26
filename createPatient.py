import sqlite3
import random

diagnosisID = 1
patientID = 1

conn = sqlite3.connect('extra/test.sqlite')

c = conn.cursor()
c2 = conn.cursor()

c.execute('SELECT id, trigger FROM triggers')

tempTriggerRow = c.fetchone()
while (tempTriggerRow != None):
	c2.execute('SELECT tr_links.id FROM dtr_links, tr_links WHERE dtr_links.diagnosis_id=? AND dtr_links.tr_link_id=tr_links.id AND tr_links.trigger_id=?', (diagnosisID, tempTriggerRow[0]))

	tempRows = c2.fetchall()
	if len(tempRows) > 0:
		tempTRLink = random.choice(tempRows)[0]

		c2.execute('INSERT INTO ptr_links (patient_id, tr_link_id) VALUES (?, ?)', (patientID,tempTRLink))

	tempTriggerRow = c.fetchone()

conn.commit()
conn.close()