import sqlite3

db = sqlite3.connect("default_v2.sqlite")
cursor = db.cursor()

# open the dicationary txt file
file = open("query_dictionary.txt", 'r')
# per line in file, add to db
line = file.readline()
while line != '':
	if line != '\n':
		cursor.execute('INSERT INTO triggers (trigger) VALUES (?)', (line.strip(),))
	line = file.readline()
file.close()

# open the order dictionary txt file
file = open("order_dictionary.txt", 'r')
# per line in file, add to db
line = file.readline()
while line != '':
	if line != '\n':
		cursor.execute('INSERT INTO orders (name) VALUES (?)', (line.strip(),))
	line = file.readline()
file.close()

db.commit()
db.close()