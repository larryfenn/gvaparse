import csv
import sqlite3
conn = sqlite3.connect('gva.db')
c = conn.cursor()

names = open('us-state-names.tsv', 'r')
reader = csv.reader(names, delimiter='\t')
names = list(reader)

# we want to populate several csvs with the following columns:
# date, city, state, age, gender
# null, null, null, "", null

# individual cvs are going to be [unharmed|injured|killed]-[nonshooting|accident|home|defense|defense3|mass|school]
# so we select

# WARNING: if exposed to the public use execute() instead to avoid SQL injection attacks

# STATUS field
casualty_types = ('Unharmed', 'Injured', 'Killed')

incident_types = ('nonshooting', 'accident', 'home', 'defense', 'defense3', 'mass', 'school')

for cas in casualty_types:
	for inc in incident_types:
		c.execute('SELECT date, city, state, age, gender, status, source, nonshooting, accident, home, defense, defense3, mass, school FROM GVA WHERE status == \"{0}\" AND {1} == \"TRUE\"'.format(cas, inc))
		with open('./gentables/{0}-{1}.csv'.format(cas, inc), 'w') as f:
			writer = csv.writer(f)
			writer.writerow(['date', 'city', 'state', 'age', 'gender', 'status', 'source', 'nonshooting', 'accident', 'home', 'defense', 'defense3', 'mass', 'school'])
			row = c.fetchone()
			while row is not None:
				newrow = list(row)
				stateid = 0;
				for i in range(len(names)):
					if names[i][2] == row[2]:
						stateid = names[i][0]
				newrow[2] = stateid
				writer.writerow(newrow)
				row = c.fetchone()

conn.close()
