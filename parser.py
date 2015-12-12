from bs4 import BeautifulSoup
import sqlite3

raw = open("results.txt", encoding="utf8").read()
soup = BeautifulSoup(raw, 'html.parser')

# row type reference:

# ID  | EVENT_NAME | LOCATION | GEOLOCATION | CITY | STATE | CONGRESS | NAME | .
# INT | TEXT       | TEXT     | TEXT        | TEXT | TEXT  | INTEGER  | TEXT | .

# .. TYPE | AGE | GENDER | STATUS | RELATIONSHIP | CHARACTERISTICS | NOTES | ...
# .. TEXT | INT | TEXT   | TEXT   | TEXT         | TEXT            | TEXT  | ...

# .. SOURCE | NONSHOOTING | ACCIDENT | HOME | DEFENSE | DEFENSE3 | MASS | SCHOOL
# .. TEXT   | TEXT        | TEXT     | TEXT | TEXT    | TEXT     | TEXT | TEXT

conn = sqlite3.connect('gva.db')
c = conn.cursor()
c.execute("CREATE TABLE GVA(id int, event_name text, location text, geolocation text, city text, state text, congress int, name text, type text, age int, gender text, status text, relationship text, characteristics text, notes text, source text, nonshooting text, accident text, home text, defense text, defense3 text, mass text, school text, suicide text, date text);")

def writeEntry(id, event_name, location, geolocation, city, state, congress, name, type, age, gender, status, relationship, characteristics, notes, source, nonshooting, accident, home, defense, defense3, mass, school, suicide, date):
	request = '{0}, \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", {6}, \"{7}\", \"{8}\", {9}, \"{10}\", \"{11}\", \"{12}\", \"{13}\", \"{14}\", \"{15}\", \"{16}\", \"{17}\", \"{18}\", \"{19}\", \"{20}\", \"{21}\", \"{22}\", \"{23}\", \"{24}\"'.format(
		id, event_name, location, geolocation, city, state, congress, name, type, age, gender, status, relationship, characteristics, notes, source, nonshooting, accident, home, defense, defense3, mass, school, suicide, date)
	c.execute("INSERT INTO GVA VALUES({0});".format(request))

for i in range(int(len(soup)/2)):
	id = soup.contents[2*i]
	doc = soup.contents[2*i + 1]
	event_name = doc.h1.string
	date = event_name.split(" ")[0]
	location = "NULL"
	geolocation = "NULL"
	city = "NULL"
	state = "NULL"
	congress = "NULL"
	name = "NULL"
	type = "NULL"
	age = "NULL"
	gender = "NULL"
	status = "NULL"
	relationship = "NULL"
	characteristics = "NULL"
	notes = "NULL"
	source = "NULL"
	nonshooting = "FALSE"
	accident = "FALSE"
	home = "FALSE"
	defense = "FALSE"
	defense3 = "FALSE"
	mass = "FALSE"
	school = "FALSE"
	suicide = "FALSE"
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
						city = state[0].strip()
						state = state[len(state) - 1].strip()
			location = location.strip()

		if (h.string == 'Incident Characteristics'):
			values = h.parent.find_all('li')
			characteristics = ""
			for v in values:
				characteristics += v.string + "\n"
				if (v.string == 'Non-Shooting Incident'):
					nonshooting = "TRUE"
				if (v.string == 'Accidental Shooting'):
					accident = "TRUE"
				if (v.string == 'Home Invasion'):
					home = "TRUE"
				if (v.string == 'Defensive Use'):
					defense = "TRUE"
				if (v.string == 'Defensive Use - Good Samaritan/Third Party'):
					defense3 = "TRUE"
				if (v.string == 'Mass Shooting (4+ victims injured or killed excluding the perpetrator, one location)'):
					mass = "TRUE"
				if (v.string == 'School Incident'):
					school = "TRUE"
				if (v.string == 'Suicide'):
					suicide = "TRUE"
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
				type = "NULL"
				name = "NULL"
				age = "NULL"
				gender = "NULL"
				status = "NULL"
				relationship = "NULL"
				entries = person.find_all('li')
				for e in entries:
					key = e.string.split(":")[0]
					value = e.string.split(":")[1].strip()
					if (key == 'Type'):
						type = value
					if (key == 'Name'):
						name = value.replace("\"","\'")
					if (key == 'Age'):
						age = value
					if (key == 'Gender'):
						gender = value
					if (key == 'Status'):
						status = value
					if (key == 'Relationship'):
						relationship = value
				writeEntry(id, event_name, location, geolocation, city, state, congress, name, type, age, gender, status, relationship, characteristics, notes, source, nonshooting, accident, home, defense, defense3, mass, school, suicide, date)

conn.commit()
conn.close()
