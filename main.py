from tkinter import *# GUI window
from tkinter import filedialog
import sys
import arduino
import _thread
import time
import os

top = Tk()
top.title("Conditioning")

loadbutton = {}
loadfile = {}
port = {}
portlist = {}
output = {}
outputlist = {}

for i in range(10):
	loadfile[i + 1] = ""
	outputlist[i + 1] = "N"

def pressbutton(count):
	global portlist
	for i in range(10):
		portlist[i + 1] = port[i + 1].get()
		if output[i + 1].get() != "":
			outputlist[i + 1] = output[i + 1].get()
	run(count)

def run(count):
	global loadfile
	global portlist
	if count <= 10:
		count += 1
		currentport = portlist[count]
		if count < 10:
			_thread.start_new_thread(run,(count,))
			
		if loadfile[count] != "":
			var = "python " + str(loadfile[count]) + " " + str(portlist[count]) + " " + str(outputlist[count]) + " " + str(count)
			os.system(var)

def load(num):
	global loadfile
	loadfile[num] = filedialog.askopenfile()
	if loadfile[num] != None:
		if num == 1:
			loadbutton1.config(bg = "#33FFFF")
		if num == 2:
			loadbutton2.config(bg = "#33FFFF")
		if num == 3:
			loadbutton3.config(bg = "#33FFFF")
		if num == 4:
			loadbutton4.config(bg = "#33FFFF")
		if num == 5:
			loadbutton5.config(bg = "#33FFFF")
		if num == 6:
			loadbutton6.config(bg = "#33FFFF")
		if num == 7:
			loadbutton7.config(bg = "#33FFFF")
		if num == 8:
			loadbutton8.config(bg = "#33FFFF")
		if num == 9:
			loadbutton9.config(bg = "#33FFFF")
		if num == 10:
			loadbutton10.config(bg = "#33FFFF")
		loadfile[num] = str(loadfile[num]).rsplit("/", 1)[1]
		loadfile[num] = str(loadfile[num]).rsplit("'", 5)[0]

# exit button function
def exit():
	top.destroy()
	sys.exit()

loadbutton1 = Button(top, text="Load", command=lambda: load(1))
loadbutton1.grid(column = 1, row = 0)
loadbutton2 = Button(top, text="Load", command=lambda: load(2))
loadbutton2.grid(column = 1, row = 1)
loadbutton3 = Button(top, text="Load", command=lambda: load(3))
loadbutton3.grid(column = 1, row = 2)
loadbutton4 = Button(top, text="Load", command=lambda: load(4))
loadbutton4.grid(column = 1, row = 3)
loadbutton5 = Button(top, text="Load", command=lambda: load(5))
loadbutton5.grid(column = 1, row = 4)
loadbutton6 = Button(top, text="Load", command=lambda: load(6))
loadbutton6.grid(column = 1, row = 5)
loadbutton7 = Button(top, text="Load", command=lambda: load(7))
loadbutton7.grid(column = 1, row = 6)
loadbutton8 = Button(top, text="Load", command=lambda: load(8))
loadbutton8.grid(column = 1, row = 7)
loadbutton9 = Button(top, text="Load", command=lambda: load(9))
loadbutton9.grid(column = 1, row = 8)
loadbutton10 = Button(top, text="Load", command=lambda: load(10))
loadbutton10.grid(column = 1, row = 9)


for i in range(10):
	Label(top, text = "Arduino: " + str(i + 1) + "  ").grid(column = 0, row = i, padx=5)

	Label(top, text = "Port: COM").grid(column = 2, row = i, padx=5)

	port[i + 1] = Entry(top)
	port[i + 1].grid(column = 3, row = i)

	Label(top, text = "Output name: ").grid(column = 4, row = i, padx=5)

	output[i + 1] = Entry(top)
	output[i + 1].grid(column = 5, row = i)

	Label(top, text = "(Optional)").grid(column = 6, row = i, padx=5)

# button for main function
startButton = Button(top, text="Start", command=lambda: pressbutton(0))
startButton.grid(column=0, row=10)

# exit button
exitButton = Button(top, text="Exit", command=exit)
exitButton.grid(column=1, row=10)

top.mainloop()  