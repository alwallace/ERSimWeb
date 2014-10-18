import sqlite3
import sys
import csv

if len(sys.argv) != 3:
	print("Use: " + sys.argv[0] + " <import file> <db>")
	exit()

importFile = open(sys.argv[1], 'r')
csv_reader = csv.DictReader(importFile)
db = sqlite3.connect(sys.argv[2])
cur = db.cursor()

for row in csv_reader:
	cur.execute('SELECT id FROM diagnosis WHERE name=?', (row['Diagnosis'],))
	diagnosis_id = -1
	result = cur.fetchall()
	if len(result) == 0:
		cur.execute('INSERT INTO diagnosis (name) VALUES (?)', (row['Diagnosis'],))
		cur.execute('SELECT last_insert_rowid()')
		diagnosis_id = cur.fetchall()[0][0]
	else:
		diagnosis_id = result[0][0]

	# check if this row already exists...
	cur.execute('SELECT quiz_materials_id FROM quiz_materials WHERE resource=? AND diagnosis_id=? AND question=? AND answer=?',
		(row['Resource'], diagnosis_id, row['Question'], row['Answer']))
	if len(cur.fetchall()) == 0:
		cur.execute('INSERT INTO quiz_materials (resource, diagnosis_id, question, answer) VALUES (?,?,?,?)', 
			(row['Resource'], diagnosis_id, row['Question'], row['Answer']))

db.commit()
cur.close()
db.close()