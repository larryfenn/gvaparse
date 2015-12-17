import csv
import sqlite3
from dateutil.parser import parse as dtparse
statepops = {}
with open('pop.csv', 'r') as f:
	reader = csv.reader(f)
	for row in reader:
		statepops[row[4]] = float(row[5])

conn = sqlite3.connect('gva.db')
c = conn.cursor()
c.execute('SELECT date, age, state, type, gender, status, characteristics FROM GVA where state != \"\" AND characteristics != \"NULL\" AND characteristics != \"\"')
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
	characteristics = entry[6].split('\n')
	for char in characteristics:
		item[char] = 1
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

from sklearn.feature_extraction import DictVectorizer
from sklearn import preprocessing
import numpy as np
vec = DictVectorizer()
X = vec.fit_transform(data).toarray()
X = preprocessing.scale(X)

n_components = 10
alpha = 100
component_thresh = 0
from sklearn import decomposition
estimator = decomposition.SparsePCA(n_components=n_components, alpha=alpha, verbose=True)
X_pca = estimator.fit(X)
newfeatures = list()
for i in range(len(X_pca.components_)):
	feature = {}
	for j in range(len(X_pca.components_[i])):
		if abs(X_pca.components_[i][j]) > component_thresh:
			feature[vec.get_feature_names()[j]] = X_pca.components_[i][j]
	newfeatures.append(feature)
print(len(newfeatures[0])) # report on how many items are in the sparse representation
for i in range(len(newfeatures)):
	print(newfeatures[i].keys())



import matplotlib.pyplot as plt


def draw(i):
	""" draw the bar graph corresponding to newfeatures[index] """
	plt.bar(range(len(newfeatures[i])), newfeatures[i].values())
	plt.xticks(range(len(newfeatures[i])), newfeatures[i].keys(), rotation='vertical')
	plt.savefig(str(i) + '.png', bbox_inches='tight')
	plt.close()
