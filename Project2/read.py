def read(posname,timename):
	posname = posname + ".POS"
	timename = timename + ".txt"

	posfile = open(posname, "r")
	timefile = open(timename, "r")

	poslist = []
	timelist = []

	for line in posfile:
		poslist.append(line)
	for line in timefile:
		timelist.append(line)

	return (poslist,timelist)