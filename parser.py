# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import sqlite3

raw = open("results.txt", "r").read()
soup = BeautifulSoup(raw, 'html.parser')

# row type reference:

# ID  | EVENT_NAME | LOCATION | GEOLOCATION | STATE | CONGRESS | NAME | TYPE | .
# INT | TEXT       | TEXT     | TEXT        | TEXT  | INTEGER  | TEXT | TEXT | .

# .. AGE | GENDER | STATUS | RELATIONSHIP | CHARACTERISTICS | NOTES | SOURCE
# .. INT | TEXT   | TEXT   | TEXT         | TEXT            | TEXT  | TEXT

conn = sqlite3.connect('gva.db')
c = conn.cursor()
c.execute("CREATE TABLE GVA(id int, event_name text, location text, geolocation text, state text, congress int, name text, type text, age int, gender text, status text, relationship text, characteristics text, notes text, source text);")

def writeEntry(id, event_name, location, geolocation, state, congress, name, type, age, gender, status, relationship, characteristics, notes, sources):
	request = '{0}, \"{1}\", \"{2}\", \"{3}\", \"{4}\", {5}, \"{6}\", \"{7}\", {8}, \"{9}\", \"{10}\", \"{11}\", \"{12}\", \"{13}\", \"{14}\"'.format(
		id, event_name, location, geolocation, state, congress, name, type, age, gender, status, relationship, characteristics, notes, source)
	c.execute("INSERT INTO GVA VALUES({0});".format(request))

for i in range(int(len(soup)/2)):
	id = soup.contents[2*i]
	doc = soup.contents[2*i + 1]
	event_name = doc.h1.string
	location = 'NA'
	geolocation = 'NA'
	state = 'NA'
	congress = 0
	name = 'NA'
	type = 'NA'
	age = 0
	gender = 'NA'
	status = 'NA'
	relationship = 'NA'
	characteristics = 'NA'
	notes = 'NA'
	source = 'NA'
	headings = doc.find_all('h2')
	# first build the entries that will be the same for all participants
	for h in headings:
		if (h.string == 'Location'):
			values = h.parent.find_all('span')
			location = ""
			for v in values:
				if v.string is not None:
					if v.string.startswith('Geolocation'):
						geolocation = v.string.split(":")[1].strip()
					else:
						location += v.string + "\n"
						state = v.string.split(",")
						state = state[len(state) - 1].strip()
			location = location.strip()

		if (h.string == 'Incident Characteristics'):
			values = h.parent.find_all('li')
			characteristics = ""
			for v in values:
				characteristics += v.string + "\n"
			characteristics = characteristics.strip()

		if (h.string == 'Notes'):
			notes = h.parent.p.string
			notes = notes.replace("\"", "\'") # to avoid table breakage

		if (h.string == 'Sources'):
			source = ""
			values = h.parent.find_all('a')
			for v in values:
				source += v.string + "\n"
			source = source.strip()

		if (h.string == 'District'):
			congress = h.next_sibling.string.split(" ")[2]

	# for each participant, create the entry
	# the loop has to be run again because we need all the other fields first
	for h in headings:
		if (h.string == 'Participants'):
			people = h.parent.find_all('ul')
			for person in people:
				entries = person.parent.find_all('li')
				for e in entries:
					key = e.string.split(":")[0]
					value = e.string.split(":")[1].strip()
					if (key == 'Type'):
						type = value
					if (key == 'Name'):
						name = value
					if (key == 'Age'):
						age = value
					if (key == 'Gender'):
						gender = value
					if (key == 'Status'):
						status = value
					if (key == 'Relationship'):
						relationship = value
				print(id)
				writeEntry(id, event_name, location, geolocation, state, congress, name, type, age, gender, status, relationship, characteristics, notes, source)

conn.commit()
conn.close()
