from sklearn import svm
import csv

def svm(filename):
	datalist = []
	length = [1,3,5,7,9]

	with open(filename + '.csv', 'r', newline='') as f:
		r = csv.reader(f)
		for i in r:
			datalist.append(i)

	for l in length:


		pos = []
		nue = []

		for i in range(length-1, 5000):
			posa = []
			for j in range(l):
				posa.append(float(datalist[i-(j - 1)][1]), float(datalist[i-(j - 1)][2]))
			pos.append(posa)
			nue.append(int(datalist[i][3]))

		f = svm.SVC()
		f.fit(pos, nue)
