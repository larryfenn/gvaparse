# python 3
# assistant for making the background data for the webpage
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
casualty_types = ('Injured', 'Killed', 'Injured\" OR status == \"Killed')

incident_types = ('accident', 'defense', 'defense3', 'mass')

for cas in casualty_types:
	for inc in incident_types:
		if (cas == 'InjuredKilled'):
			cas = 'Injured\" OR status == \"Killed' # SQL injcetion hack
		c.execute('SELECT date, city, state, age, gender, status, source, nonshooting, accident, home, defense, defense3, mass, school FROM GVA WHERE (status == \"{0}\") AND {1} == \"TRUE\"'.format(cas, inc))
		if (cas == 'Injured\" OR status == \"Killed'):
			cas = 'InjuredKilled' # fixing my SQL injection hack
		casualtiesbystate = [0]*79 # us-state names
		with open('./gentables/{0}-{1}.csv'.format(cas, inc), 'w') as f:
			writer = csv.writer(f, lineterminator='\n') # windows compatability
			writer.writerow(['date', 'city', 'state', 'age', 'gender', 'status', 'source', 'accident', 'defense', 'defense3', 'mass'])
			row = c.fetchone()
			while row is not None:
				newrow = list(row)
				stateid = 0;
				for i in range(len(names)):
					if names[i][2] == row[2]:
						stateid = names[i][0]
				casualtiesbystate[int(stateid)] += 1
				newrow[2] = stateid
				writer.writerow(newrow)
				row = c.fetchone()
		output = open('./gentables/{0}-{1}-statetotals.tsv'.format(cas, inc), 'w')
		statewriter = csv.writer(output, delimiter='\t')
		statewriter.writerow(['id', 'count'])
		for id in range(len(casualtiesbystate)):
			statewriter.writerow([id, casualtiesbystate[id]])
		output.close()

conn.close()
