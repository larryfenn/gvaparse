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

c.execute('SELECT status, characteristics, gender FROM GVA where type == \"Perpetrator\"')
entry = c.fetchone()
while (entry is not None):
	# NOTE: many statuses have multiple conditions!
	status = entry[0]
	characteristics = entry[1].split('\n')
	gender = entry[2]
	for tag in characteristics:
		if ("Shot" not in tag):
			if ("Unharmed" == status):
				addToDict(unharmed, tag)
			if ("Injured" == status):
				addToDict(injured, tag)
			if ("Killed" == status):
				addToDict(killed, tag)
			if ("Arrested" == status):
				addToDict(arrested, tag)
			if ("Male" == gender):
				addToDict(male, tag)
			if ("Female" == gender):
				addToDict(female, tag)
			addToDict(total, tag)
	entry = c.fetchone()
conn.close()

# visualizing code
def plotHist(input, select):
	d = dict(sorted(input.iteritems(), key = operator.itemgetter(1), reverse = True)[:select])
	x = np.arange(len(d))
	plt.bar(x, d.values(), align='center', width=.5)
	plt.xticks(x, d.keys())
	plt.show()


def plotPie(input, colormapscale=1, bottom=.75):
	maxval = sum(input.values())
	minval = 0
	d = sorted(input.iteritems(), key = operator.itemgetter(1), reverse = True)
	labels = []
	sizes = []
	running = 0
	for i in d:
		labels.append(i[0])
		sizes.append(i[1])
		running += i[1]
		if running > (bottom*maxval):
			minval = i[1]
			break
	labelcolors = list()
	for l in labels:
		labelcolors.append(total.keys().index(l))
	labels.append("Other".format(100*(1 - running/float(maxval))))
	labelcolors.append(len(total.keys()) + 1)
	sizes.append(maxval - running)
	percents = 100.*np.array(sizes)/np.array(sizes).sum()
	labels = ['{1:1.2f}% - {0}'.format(i, j) for i, j in zip(labels, percents)]
	norm = matplotlib.colors.Normalize(0, len(total.keys()) + 1)
	cmap = matplotlib.cm.get_cmap('Set1')
	fig = pylab.figure()
	figlegend = pylab.figure(figsize=(3,2))
	ax = fig.add_subplot(111)
	patches, texts = ax.pie(sizes, startangle=90, colors=cmap(norm(labelcolors)))
	ax.axis('equal')
	figlegend.legend(patches, labels, 'center')
	fig.show()
	fig.savefig('f.png', bbox_inches='tight')
	figlegend.show()
