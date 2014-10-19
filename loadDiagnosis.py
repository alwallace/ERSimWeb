import sqlite3
import sys
import csv

try:
    __file__
except:
    sys.argv = [sys.argv[0], 'ERSim Lists Baseline.csv', './ersim/extra/ersim.sqlite']

def query_db(conn, query, args=(), one=False):
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def commit_db(conn, query, args=()):
    cur = conn.execute(query, args)
    conn.commit()

def lastid_db(conn):
    return query_db(conn, "SELECT last_insert_rowid()", (), True)[0]


if len(sys.argv) != 3:
	print("Use: " + sys.argv[0] + " <import file> <db>")
	exit()

importFile = open(sys.argv[1], 'r')
csv_reader = csv.DictReader(importFile)
conn = sqlite3.connect(sys.argv[2])
NORMAL_DIAGNOSIS = "Normal"

diagnosisIDs = {}
for diagnosis in csv_reader.fieldnames:
	# Check that its not actually the Setting column
	if not diagnosis == "Setting":
		# Create the diagnosis
		# first check if they exist already
		result = query_db(conn, "SELECT id FROM diagnosis WHERE name=?", (diagnosis,), True)
		if result is None:
			# if not then create it
			commit_db(conn, "INSERT INTO diagnosis (name) VALUES (?)", (diagnosis,))
			result = [lastid_db(conn)]
		diagnosisIDs[diagnosis] = result[0]

print "Diagnosis: "
print diagnosisIDs
print ""

excludedSettings = ['age range', 'gender']
for row in csv_reader:
	print row
	# Get the trigger from teh setting column
	if not row['Setting'] in excludedSettings:
		# Check if it exists in DB already
		result = query_db(conn, "SELECT id FROM triggers WHERE trigger=?", (row['Setting'],), True)
		if result is None:
			# then create it
			commit_db(conn, "INSERT INTO triggers (trigger) VALUES (?)", (row['Setting'],))
			result = [lastid_db(conn)]
		triggerID = result[0]

		for diagnosis in diagnosisIDs.keys():
			diagnosisID = diagnosisIDs[diagnosis]

			# if there is a non-normal response then add it.
			if not row[diagnosis] == '':
				# get teh responses for this diagnosis and split them
				responses = row[diagnosis].split(';')
				for response in responses:
					# Check if the response exists in DB already
					result = query_db(conn, "SELECT id FROM responses WHERE response=?", (response,), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO responses (response) VALUES (?)", (response,))
						result = [lastid_db(conn)]
					responseID = result[0]

					# Create the TR link
					# Check if the link exists in DB already
					result = query_db(conn, "SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO tr_links (trigger_id, response_id) VALUES (?,?)", (triggerID, responseID))
						result = [lastid_db(conn)]
					trLinkID = result[0]

					# Create the dtr_link
					# check if the dtr link exists
					result = query_db(conn, "SELECT id FROM dtr_links WHERE diagnosis_id=? AND tr_link_id=?", (diagnosisID, trLinkID), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO dtr_links (diagnosis_id, tr_link_id) VALUES (?,?)", (diagnosisID, trLinkID))
						result = [lastid_db(conn)]
					dtrLinkID = result[0]

			else:
				# use the "normal diagnosis" column to add these as responses
				# get teh responses for this diagnosis and split them
				responses = row[NORMAL_DIAGNOSIS].split(';')
				for response in responses:
					# Check if the response exists in DB already
					result = query_db(conn, "SELECT id FROM responses WHERE response=?", (response,), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO responses (response) VALUES (?)", (response,))
						result = [lastid_db(conn)]
					responseID = result[0]

					# Create the TR link
					# Check if the link exists in DB already
					result = query_db(conn, "SELECT id FROM tr_links WHERE trigger_id=? AND response_id=?", (triggerID, responseID), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO tr_links (trigger_id, response_id) VALUES (?,?)", (triggerID, responseID))
						result = [lastid_db(conn)]
					trLinkID = result[0]

					# Create the dtr_link
					# check if the dtr link exists
					result = query_db(conn, "SELECT id FROM dtr_links WHERE diagnosis_id=? AND tr_link_id=?", (diagnosisID, trLinkID), True)
					if result is None:
						# then create it
						commit_db(conn, "INSERT INTO dtr_links (diagnosis_id, tr_link_id) VALUES (?,?)", (diagnosisID, trLinkID))
						result = [lastid_db(conn)]
					dtrLinkID = result[0]

conn.commit()
conn.close()

