# python 2.7
# possible bad fields from sql queries:
# date:
# age: ""
# state: ""
# type:
# gender: "NULL"
# status: "NULL"
# relationship: "NULL"
# characteristics: "NULL", ""
import csv
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from dateutil.parser import parse as dtparse
statepops = {}
with open('pop.csv', 'r') as f:
	reader = csv.reader(f)
	for row in reader:
		statepops[row[4]] = float(row[5])

conn = sqlite3.connect('gva.db')
c = conn.cursor()
c.execute('SELECT date, age, state, type, gender, status, characteristics FROM GVA where state != \"\" AND age != \"\" AND type == \"Victim\" AND characteristics != \"NULL\" AND characteristics != \"\"')
data = []

stateabbrevs = {}
with open('us-state-names.tsv', 'r') as f:
	reader = csv.reader(f, delimiter='\t')
	for row in reader:
		stateabbrevs[row[2]] = row[1]

statelabels = []

entry = c.fetchone()
while (entry is not None):
	item = {}
	statelabels.append(entry[2])
	item["age"] = float(entry[1]) # float because we don't want to treat this as a categorical
	item["state"] = entry[2]
	item["gender"] = entry[4]
	item["status"] = entry[5]
	if "Unharmed" in entry[5]:
		item["status"] = 0
	if "Injured" in entry[5]:
		item["status"] = 1
	if "Killed" in entry[5]:
		item["status"] = 2
	char = entry[6]
	item["Accident"] = "F"
	item["Defense"] = "F"
	if ("Accident" in char):
		item["Accident"] = "T"
	if ("Defens" in char): # to catch "Defensive", among others
		item["Defense"] = "T"
	data.append(item)
	entry = c.fetchone()
conn.close()

print(len(data)) # get a sense for how much data we have to work with

def addToDict(dict, key, value):
	""" accumulates values in an integer-valued dict """
	if key in dict.keys():
		dict[key] += value
	else:
		dict[key] = value

# scatterplot of just accidents and defenses
accident = {}
naccident = {}
for d in data:
	if (d['Accident'] == 'T'):
		addToDict(accident, d['state'], 1)
	else:
		addToDict(naccident, d['state'], 1)


# first make a scatterplot of 'legitimate' (defense) and 'illegitimate' (non-accident non-defense) uses
defense = {}
ndefense = {} # not defense
nadefense = {} # neither defense nor accident
for d in data:
	if (d['Defense'] == 'T'):
		addToDict(defense, d['state'], 1)
	else:
		addToDict(ndefense, d['state'], 1)
		if (d['Accident'] == 'F'):
			addToDict(nadefense, d['state'], 1)

x = []
y = []
labels = []
# scatterplot 1: accident vs. defense for fifty states
for i in statepops:
	if i in defense:
		labels.append(stateabbrevs[i])
		x.append(1000000*defense[i]/statepops[i])
		y.append(1000000*accident[i]/statepops[i])

fig, ax = plt.subplots()
ax.scatter(x, y)
for i, txt in enumerate(labels):
	ax.annotate(txt, (x[i], y[i]))


#from sklearn.feature_extraction import DictVectorizer
#from sklearn import preprocessing
#vec = DictVectorizer()
#data = vec.fit_transform(data).toarray()
#data = preprocessing.scale(data)
# Authors: Gael Varoquaux, Nelle Varoquaux
# License: BSD 3 clause

import time
import matplotlib.pyplot as plt
import numpy as np

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import SpectralClustering
from sklearn.neighbors import kneighbors_graph

n_samples = len(labels)
X = np.vstack((x, y))
X = X.T
# Create a graph capturing local connectivity. Larger number of neighbors
# will give more homogeneous clusters to the cost of computation
# time. A very large number of neighbors gives more evenly distributed
# cluster sizes, but may not impose the local manifold structure of
# the data
knn_graph = kneighbors_graph(X, 30, include_self=False)

connectivity = knn_graph
n_clusters = 2
plt.figure(figsize=(10, 4))
for index, linkage in enumerate(('average', 'complete', 'ward')):
	plt.subplot(1, 3, index + 1)
#	model = AgglomerativeClustering(linkage=linkage,
#	                                connectivity=connectivity,
#	                                n_clusters=n_clusters)
	model = SpectralClustering(n_clusters=n_clusters)
	t0 = time.time()
	model.fit(X)
	elapsed_time = time.time() - t0
	plt.scatter(X[:, 0], X[:, 1], c=model.labels_,
	            cmap=plt.cm.spectral)
	plt.title('linkage=%s (time %.2fs)' % (linkage, elapsed_time),
	          fontdict=dict(verticalalignment='top'))
	plt.axis('equal')
	plt.axis('off')

	plt.subplots_adjust(bottom=0, top=.89, wspace=0,
	                    left=0, right=1)
	plt.suptitle('n_cluster=%i, connectivity=%r' %
	             (n_clusters, connectivity is not None), size=17)


taggedx = []
taggedy = []
taggedlabels = []
for i in range(len(model.labels_)):
	if (model.labels_[i] == 1):
		taggedx.append(x[i])
		taggedy.append(y[i])
		taggedlabels.append(labels[i])

# scatterplot 2: accident vs. defense for fifty states without the noise
fig, ax = plt.subplots()
ax.scatter(taggedx, taggedy)
for i, txt in enumerate(taggedlabels):
	ax.annotate(txt, (taggedx[i], taggedy[i]))

plt.show()
