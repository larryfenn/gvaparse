import sqlite3
conn = sqlite3.connect('gva.db')
c = conn.cursor()


def search(query):
	results = 0
	total = 0
	c.execute('SELECT characteristics FROM GVA')
	entry = c.fetchone()
	while (entry is not None):
		total += 1
		characteristics = entry[0].split("\n")
		for tag in characteristics:
			if query in tag:
				results += 1
				break
	return results, results/total
