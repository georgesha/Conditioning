from tkinter import *# GUI window
from tkinter import ttk
from tkinter import filedialog
import sys
import arduino
import _thread

top = Tk()
top.title("Conditioning")

loadfile = {}
for i in range(10):
	loadfile[i + 1] = ""
countload = 1
def pressbutton(count):
	global loadfile
	if count <= 10:
		count += 1

		if count < 10:
			_thread.start_new_thread(pressbutton,(count,))
		if loadfile[count] != "":
			arduino.load(loadfile[count])



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

loadbutton = {}
for i in range(10):
	Label(top, text = "Arduino: " + str(i + 1) + "  ").grid(column = 0, row = i, padx=5)
	
	loadbutton[i + 1] = Button(top, text="Start", command=load)
	loadbutton[i + 1].grid(column=1, row=i)

# button for main function
startButton = Button(top, text="Start", command=lambda: pressbutton(0))
startButton.grid(column=0, row=10)

# exit button
exitButton = Button(top, text="Exit", command=exit)
exitButton.grid(column=1, row=10)

top.mainloop()