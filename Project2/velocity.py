def cal_v(data):
	length = len(data) - 2
	if length > 1:
		


filename = "out"

datalist = []

with open(filename + '.csv', 'r', newline='') as f:
	r = csv.reader(f)
	for i in r:
		datalist.append(i)


'''
# movement of x y

xlist = []
ylist = []

for i in datalist:
	xlist.append([int(i[1]),int(i[3])])
	ylist.append([int(i[2]),int(i[3])])

length = 4
'''