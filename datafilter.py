# python 2.7
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pylab
import operator
import sqlite3
conn = sqlite3.connect('gva.db')
c = conn.cursor()

names = open('us-state-names.tsv', 'r')
reader = csv.reader(names, delimiter='\t')
names = list(reader)

# first we need to build a collection of all the possible characteristics.
# lots of categorical variables: state, type (victim|perp), gender (male|female|null), status (killed|injured|unharmed), relationship (?? also need to filter those), characteristics

# first pass: build a library of all possible characteristics tags
# and collect them all in a dict
total = {}
unharmed = {}
injured = {}
killed = {}
arrested = {}
male = {}
female = {}
def addToDict(dict, key):
	if (key in dict):
		dict[key] += 1
	else:
		dict[key] = 1

# filtering code: edit this as you please:
c.execute('SELECT status, characteristics, gender FROM GVA')
entry = c.fetchone()
while (entry is not None):
	# NOTE: many statuses have multiple conditions!
	status = entry[0]
#	characteristics = entry[1].encode('latin-1').split('\n')
	characteristics = entry[1].split('\n')
	gender = entry[2]
	for tag in characteristics:
		if ("Unharmed" in status):
			addToDict(unharmed, tag)
		if ("Injured" in status):
			addToDict(injured, tag)
		if ("Killed" in status):
			addToDict(killed, tag)
		if ("Arrested" in status):
			addToDict(arrested, tag)
		if ("Male" in gender):
			addToDict(male, tag)
		if ("Female" in gender):
			addToDict(female, tag)
		addToDict(total, tag)
	entry = c.fetchone()

# in the original data set characteristics is a bunch of strings separated by newlines
# we need to turn that into one-hot
# the rest of the categorical variables are left as-is
encoding = {}
for i in range(len(total.keys())):
	code = [0]*len(total.keys())
	code[i] = 1
	encoding[total.keys()[i]] = code
with open('encoding.csv', 'w') as f:
	w = csv.DictWriter(f, encoding.keys())
	w.writeheader()
	w.writerow(encoding)

# filter database into csv for data filtering.
# the two model ideas i have are about states and the relation to the other variables
# date is brought along in case i want to do time series analysis
# so we have to insist that states are nonempty
c.execute('SELECT state, type, age, gender, status, relationship, characteristics, date FROM GVA where state != \"\"')

with open('modeldata.csv', 'w') as f:
	writer = csv.writer(f, lineterminator='\n') # windows compatability
	writer.writerow(['state, type, age, gender, status, relationship, characteristics, date'])
	entry = c.fetchone()
	while (entry is not None):
		# need to match all the characteristics with their one-hot equivalents, and sum up
		charcode = [0]*len(total.keys())
		characteristics = entry[6].encode('latin-1').split('\n')
		for char in characteristics:
			charcode = [x + y for x, y in zip(charcode, encoding[char])]
		# now we format the list of zeroes and ones as simply "0010101"
		charcodestr = ""
		for char in charcode:
			charcodestr += str(char)
		row = list(entry)
		row[6] = charcodestr
		writer.writerow(row)
		entry = c.fetchone()
conn.close()

# visualizing code
def plotHist(input, select):
	d = dict(sorted(input.iteritems(), key = operator.itemgetter(1), reverse = True)[:select])
	x = np.arange(len(d))
	plt.bar(x, d.values(), align='center', width=.5)
	plt.xticks(x, d.keys())
	plt.show()

def plotPie(input, colormapscale=1):
	maxval = sum(input.values())
	minval = 0
	d = sorted(input.iteritems(), key = operator.itemgetter(1), reverse = True)
	# weed out the bottom 20% and lump into one:
	labels = []
	sizes = []
	running = 0
	for i in d:
		labels.append(i[0])
		sizes.append(i[1])
		running += i[1]
		if running > (.75*maxval):
			minval = i[1]
			break
	labels.append("Bottom {0:.0f}%".format(100*(1 - running/float(maxval))))
	sizes.append(maxval - running)
	norm = matplotlib.colors.Normalize(minval, colormapscale * d[0][1])
	cmap = matplotlib.cm.get_cmap('Set1')
	fig = pylab.figure()
	figlegend = pylab.figure(figsize=(3,2))
	ax = fig.add_subplot(111)
	patches, texts = ax.pie(sizes, startangle=90, colors=cmap(norm(sizes)))
	ax.axis('equal')
	figlegend.legend(patches, labels, 'center')
	fig.show()
	figlegend.show()

