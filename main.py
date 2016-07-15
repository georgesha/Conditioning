from tkinter import *# GUI window
from tkinter import ttk
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
countload = 1

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
			var = "python " + str(loadfile[count]) + " " + str(portlist[count]) + " " + str(outputlist[count])
			os.system(var)

def load():
	global loadfile
	global countload
	loadfile[countload] = filedialog.askopenfile()
	loadfile[countload] = str(loadfile[countload]).rsplit("/", 1)[1]
	loadfile[countload] = str(loadfile[countload]).rsplit("'", 5)[0]
	countload += 1

# exit button function
def exit():
	top.destroy()
	sys.exit()



for i in range(10):
	Label(top, text = "Arduino: " + str(i + 1) + "  ").grid(column = 0, row = i, padx=5)
	
	loadbutton[i + 1] = Button(top, text="Load", command=load)
	loadbutton[i + 1].grid(column=1, row=i)

	Label(top, text = "Port: COM").grid(column = 2, row = i, padx=5)

	port[i + 1] = Entry(top)
	port[i + 1].grid(column=3, row=i)

	Label(top, text = "Output name: ").grid(column = 4, row = i, padx=5)

	output[i + 1] = Entry(top)
	output[i + 1].grid(column=5, row=i)

	Label(top, text = "(Optional)").grid(column = 6, row = i, padx=5)


# button for main function
startButton = Button(top, text="Start", command=lambda: pressbutton(0))
startButton.grid(column=0, row=10)

# exit button
exitButton = Button(top, text="Exit", command=exit)
exitButton.grid(column=1, row=10)

top.mainloop()