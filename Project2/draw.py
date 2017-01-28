import matplotlib.pyplot as plt
import csv

datalist = []

filename = "out"

with open(filename + '.csv', 'r', newline='') as f:
	r = csv.reader(f)
	for i in r:
		datalist.append(i)

dl_p = []
dl_n = []

for i in datalist:
	if int(i[3]) == 1:
		dl_p.append(i)
	else:
		dl_n.append(i)

x_p = [int(data[1]) for data in dl_p]
y_p = [int(data[2]) for data in dl_p]

x_n = [int(data[1]) for data in dl_n]
y_n = [int(data[2]) for data in dl_n]

dl_times = []

tmp = []


for i in range(len(dl_p)):
	dl_p[i] = [dl_p[i][1],dl_p[i][2]]

for i in dl_p:
	if i not in tmp:
		tmp.append(i)
		datacount = [int(i[0]),int(i[1]),dl_p.count(i)]
		dl_times.append(datacount)


plt.plot(x_n,y_n, "ko")
#plt.plot(x_p,y_p, "wo")


times = [10,20,30,40,50]
color = ["ro","bo","go","yo","co","mo",]

for i in times:
	x = []
	y = []

	for j in dl_times:
		if j[2] >= i:
			x.append(j[0])
			y.append(j[1])

	plt.plot(x, y, color[times.index(i)])		

plt.show()
