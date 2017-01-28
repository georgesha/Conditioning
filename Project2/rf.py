from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
import csv
import math

filename = "out"

datalist = []
length = [1,4,6,7,9,13,17,25,39,49,61]

with open(filename + '.csv', 'r', newline='') as f:
	r = csv.reader(f)
	for i in r:
		datalist.append(i)

pos = []
nue = []

for l in length:

	pos = []
	nue = []

	hl = math.floor(l/2)

	for i in range(l-1, 10000):
		posa = []
		for j in range(l):
			posa.append(float(datalist[i - (j - 1)][1]))
			posa.append(float(datalist[i - (j - 1)][2]))
			#posa.append(int(datalist[i-(j - 1)][3]))

		if l > 1:
			for j in range(hl):
				posa.append(int(datalist[i - hl - 1][3]))

		pos.append(posa)
		nue.append(int(datalist[i][3]))



	testpos = []
	testnue = []

	pcount = 0

	for i in range(l + 10000, l + 15000):
		testposa = []
		for j in range(l):
			testposa.append(float(datalist[i-(j - 1)][1]))
			testposa.append(float(datalist[i-(j - 1)][2]))
			#testposa.append(int(datalist[i-(j - 1)][3]))

		if l > 1:
			for j in range(hl):
				testposa.append(int(datalist[i - hl - 1][3]))

		testpos.append(testposa)
		testnue.append(int(datalist[i][3]))
		if int(datalist[i][3]) == 1:
			pcount = pcount + 1


	
	f = RandomForestClassifier(n_estimators=10)
	f = f.fit(pos, nue)
	

	'''
	f = svm.SVC(kernel="rbf")
	f.fit(pos, nue)
	'''

	'''
	accu = f.score(testpos,testnue)

	print("Length: " + str(l))
	print("accuracy: " + str(accu))
	'''

	# test
	
	result = f.predict(testpos)

	fpr, tpr, thresholds = metrics.roc_curve(testnue, result, pos_label=1)
	auc = metrics.auc(fpr, tpr)

	print(auc)

	'''
	count = 0
	p = 0
	for i in range(len(result)):
		if result[i] == 1:
			p = p + 1
		if result[i] == testnue[i]:
			count = count + 1
	print("Length: " + str(l))
	print("accuracy is: " + str(count/len(result)))
	print("positive: " + str(p/pcount))
	'''