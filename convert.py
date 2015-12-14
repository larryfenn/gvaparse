import csv
import sqlite3
conn = sqlite3.connect('gva.db')
c = conn.cursor()

names = open('us-state-names.tsv', 'r')
reader = csv.reader(names, delimiter='\t')
names = list(reader)

c.execute('select * from gva where status == \"Killed\"')
row = c.fetchone()
casualtiesbystate = [0]*79
counter = 0
with open('./gentables/suicide.csv', 'w') as f:
	writer = csv.writer(f, lineterminator='\n')
	while (row is not None):
		counter += 1
		characteristics = row[13]
		if ("Suicide" in characteristics):
			newrow = list(row)
			stateid = 0
			for i in range(len(names)):
				if names[i][2] == row[2]:
					stateid = names[i][0]
			casualtiesbystate[int(stateid)] += 1
			newrow[2] = stateid
			writer.writerow(newrow)
		row = c.fetchone()
output = open('./gentables/suicide-statetotals.tsv', 'w')
statewriter = csv.writer(output, delimiter='\t')
statewriter.writerow(['id', 'count'])
for id in range(len(casualtiesbystate)):
	statewriter.writerow([id, casualtiesbystate[id]])
output.close()


conn.close()
