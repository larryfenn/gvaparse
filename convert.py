import csv
import sqlite3
conn = sqlite3.connect('gva.db')
c = conn.cursor()

names = open('us-state-names.tsv', 'r')
reader = csv.reader(names, delimiter='\t')
names = list(reader)

c.execute('SELECT date, city, state, age, gender, status, source, nonshooting, accident, home, defense, defense3, mass, school, characteristics FROM GVA WHERE (status == \"Killed\")')
casualtiesbystate = [0]*79
counter = 0
with open('suicide.csv', 'w') as f:
	writer = csv.writer(f, lineterminator='\n')
	writer.writerow(['date', 'city', 'state', 'age', 'gender', 'status', 'source', 'accident', 'defense', 'defense3', 'mass'])
	row = c.fetchone()
	while (row is not None):
		counter += 1
		characteristics = row[14]
		try:
			if ("Suicide" in characteristics):
				newrow = list(row)
				stateid = 0
				for i in range(len(names)):
					if names[i][2] == row[2]:
						stateid = names[i][0]
				casualtiesbystate[int(stateid)] += 1
				newrow[2] = stateid
				writer.writerow(newrow)
		except:
			print(":(")
		row = c.fetchone()
output = open('suicide-statetotals.tsv', 'w')
statewriter = csv.writer(output, delimiter='\t')
statewriter.writerow(['id', 'count'])
for id in range(len(casualtiesbystate)):
	statewriter.writerow([id, casualtiesbystate[id]])
output.close()


conn.close()
