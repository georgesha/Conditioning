
def write(poslist,timelist):

	pl = []
	tl = []

	for i in poslist:
		i = i.strip('\n')
		li = i.split(" ")
		count = li.count("")
		if count > 0:
			for j in range(count):
				li.remove("")
		if li != []:
			if li[0].isdigit():
				if len(li) == 3:
					pl.append(li)
				else:
					if int(li[2]) > int(li[4]):
						del li[2]
						del li[1]
					else:
						del li[4]
						del li[3]
					pl.append(li)

	for i in timelist:
		i = i.strip('\n')
		if i != "timestamp":
			tl.append(float(i))

	poslength = len(pl)
	timelength = len(tl)

	i = 0
	j = 0

	while i < poslength and j < timelength:
		print(j)
		if float(pl[i][0]) < tl[j]:
			i = i + 1
		if float(pl[i][0]) >= tl[j]:
			if len(pl[i - 1]) == 3:
				pl[i - 1].append(1)
			j = j + 1

	for i in range(poslength):
		if len(poslist[j]) == 3:
			pl[j].append(0)

	with open('out.csv', 'w', newline='') as f:
		w = csv.writer(f)
		for i in pl:
			w.writerow(i)