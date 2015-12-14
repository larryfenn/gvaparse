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
import numpy as np
import sqlite3
from dateutil.parser import parse as dtparse
us = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

conn = sqlite3.connect('gva.db')
c = conn.cursor()
c.execute('SELECT date, age, state, type, gender, status, relationship, characteristics FROM GVA where state != \"\" AND age != \"\" AND type == \"Victim\" AND characteristics != \"NULL\" AND characteristics != \"\"')
data = []
statelabels = []
stateFlag = []
state1 = "Texas"
state2 = "Illinois"

entry = c.fetchone()
while (entry is not None):
	item = {}
	statelabels.append(entry[2])
	item["age"] = float(entry[1])
	item["state"] = entry[2]
	item["gender"] = entry[4]
	item["status"] = entry[5]
	if "Unharmed" in entry[5]:
		item["status"] = 0
	if "Injured" in entry[5]:
		item["status"] = 1
	if "Killed" in entry[5]:
		item["status"] = 2
	characteristics = entry[7].split('\n')
	item["Accident"] = "F"
	item["Defense"] = "F"
	for char in characteristics:
		if ("Accident" in char):
			item["Accident"] = "T"
		if ("Defense" in char):
			item["Defense"] = "T"
	data.append(item)
	if entry[2] == state1:
		stateFlag.append(1)
	elif entry[2] == state2:
		stateFlag.append(2)
	else:
		stateFlag.append(0)
	#
	entry = c.fetchone()
conn.close()

print(len(data)) # get a sense for how much data we have to work with

from sklearn.feature_extraction import DictVectorizer
from sklearn import preprocessing
vec = DictVectorizer()
data = vec.fit_transform(data).toarray()
data = preprocessing.scale(data)

###
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

y = np.asarray(stateFlag)
target_names = np.asarray([state1, state2, 'Rest of country'])

pca = PCA(n_components=2)
data_r = pca.fit(data).transform(data)


# Percentage of variance explained for each components
print('explained variance ratio (first two components): %s'
      % str(pca.explained_variance_ratio_))

plt.figure()
for c, i, target_name in zip("rgb", [0, 1, 2], target_names):
    plt.scatter(data_r[y == i, 0], data_r[y == i, 1], c=c, label=target_name)
plt.legend()
plt.title('PCA of dataset')

plt.show()
