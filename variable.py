"""
 Variable ratio operant conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting reward 
 according to whether the rat has achieved the criterion
 where the criterion for each trial is randomly selected from a certain range

 The circuit:
 * Red LED attached from pin 11 to +5V
 * 560 Ohm resistors attached from pin 11 to GND
 * Servo attached to pin 13
 * Button attached to pin 3

 """

# Import all needed libraries
import tkinter # GUI window
from time import sleep # delay to achieve time sequence
import pyfirmata # Arduino Uno board
import csv # saving information to files
import sys # correctly shut down the program
import time # give the rative time to record actions
import datetime
import math # help do calculation when getting ralative time
import random # random select the criterion for each trial
import arduino


def main(port,output,num):
	portname = 'COM' + str(port)
	board = pyfirmata.Arduino(portname)

	if output == "N":
		now = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
		output = "output_variable_" + str(now) + ".txt"

	open(output, 'w').close()
	title = open(str(output), 'a', newline='')
	title.write("Arduino " + str(num) + " Variable Ratio" + "\n")
	title.close()		

	# Using iterator thread to avoid buffer overflow
	it = pyfirmata.util.Iterator(board)
	it.start()

	# Define pins
	operantPin = board.get_pin('d:3:i')
	csPin = board.get_pin('d:11:o')
	usPin = 13
	board.digital[usPin].mode = pyfirmata.SERVO

	# start time of the experiment
	starttime = time.time()

	# Initialize main windows with title and size
	top = tkinter.Tk()
	top.title("Arduino " + str(num) + " Variable Ratio")

	#create the checkbox for pre-test
	tkinter.Label(top, text = "Pretest: Y/N").grid(column = 1, row = 1)
	preEntry = tkinter.Entry(top)
	preEntry.grid(column=2, row=1) # to manage the location on window
	preEntry.focus_set()

	tkinter.Label(top, text = "Load: Y/N").grid(column = 1, row = 2)
	loadEntry = tkinter.Entry(top)
	loadEntry.grid(column = 2, row = 2)
	loadEntry.focus_set()



	# the interval between receive and act
	tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 3)
	intervalEntry = tkinter.Entry(top)
	intervalEntry.grid(column = 2, row = 3)
	intervalEntry.focus_set()

	# how long will the feeding last
	tkinter.Label(top, text = "Duration: ").grid(column = 1, row = 4)
	durationEntry = tkinter.Entry(top)
	durationEntry.grid(column = 2, row = 4)
	durationEntry.focus_set()

	# range
	tkinter.Label(top, text = "Range: ").grid(column = 1, row = 5)
	rangeminEntry = tkinter.Entry(top)
	rangeminEntry.grid(column = 2, row = 5)
	rangeminEntry.focus_set()
	tkinter.Label(top, text = " to ").grid(column = 3, row = 5)
	rangemaxEntry = tkinter.Entry(top)
	rangemaxEntry.grid(column = 4, row = 5)
	rangemaxEntry.focus_set()

	# list of times
	tkinter.Label(top, text = "List of times: ").grid(column = 1, row = 6)
	listEntry = tkinter.Entry(top)
	listEntry.grid(column = 2, row = 6)
	listEntry.focus_set()
	tkinter.Label(top, text = " Please separate with blank").grid(column = 3, row = 6)

	# create the checkbox for range or List
	tkinter.Label(top, text = "Mode: L/R").grid(column = 1, row = 7)
	modeEntry = tkinter.Entry(top)
	modeEntry.grid(column = 2, row = 7)
	modeEntry.focus_set()

	tkinter.Label(top, text = "trial times: ").grid(column = 1, row = 8)
	trialEntry = tkinter.Entry(top)
	trialEntry.grid(column = 2, row = 8)
	tkinter.Label(top, text = "times").grid(column = 3, row = 8)



	tkinter.Label(top, text = "length: ").grid(column = 1, row = 9)
	lengthEntry = tkinter.Entry(top)
	lengthEntry.grid(column = 2, row = 9)
	tkinter.Label(top, text = "hours").grid(column = 3, row = 9)

	systemlist = [board,top,starttime,output,num]
	entrylist = [preEntry,loadEntry,intervalEntry,durationEntry,rangeminEntry,rangemaxEntry,listEntry,modeEntry,trialEntry,lengthEntry]
	pinlist = [operantPin,csPin,usPin]

	# Create Start and Exit button

	# button for main function
	startButton = tkinter.Button(top, text="Start", command=lambda: pressbutton(systemlist,entrylist,pinlist,startButton))
	startButton.grid(column=1, row=10)

	# exit button
	exitButton = tkinter.Button(top, text="Exit", command=lambda: exit(board,top))
	exitButton.grid(column=2, row=10)

	#start and open the window
	top.mainloop()

# main function
def pressbutton(systemlist,entrylist,pinlist,startButton):
	# create a variable to achieve correct detection of the state of button
	# it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
	# and it will be changed to zero again only when the button is released
	# after it back to zero, another press will be detected and count as active press
	# meanwhile, this variable can count for the rising and falling edge of button

	currenttimes = 0 # the times that the rat already press
	upanddown = 0
	timeslist = []
	rangemin = 0
	rangemax = 0

	trialtimes = math.inf
	timelength = math.inf

	if entrylist[8].get() != "": # trial mode
		trialtimes = int(entrylist[8].get())
	if entrylist[9].get() != "":
		timelength = float(entrylist[9].get()) * 3600 # change to second	
	# disable the start button to avoid double-click during executing
	startButton.config(state=tkinter.DISABLED)
	
	# If user choose to pre-test
	# automatically start a trial that implement all the hardware
	# in order to check basic settings	
	if entrylist[0].get() == "Y":
		inputlist = [pinlist[0]]
		outputlist = [pinlist[1],pinlist[2]]
		arduino.pretest(systemlist[0], systemlist[1], inputlist, outputlist)
	# implement the experiment						
	else:
		# whether load the configuration
		# read from existing configuration and print them out
		if entrylist[1].get() == "Y":
			with open('configuration_variable.csv', 'r', newline='') as f:
				r = csv.reader(f)
				data = None
				count = 0
				for row in r:
					if count == 1:
						data = row
					count += 1
				interval = math.floor(float(data[0]))
				duration= math.floor(float(data[1]))
				print("read result: ")
				print("interval: " + data[0])
				print("duration: " + data[1])
				if data[2] != "NA":
					rangemin = math.floor(float(data[2]))
					rangemax = math.floor(float(data[3]))
					print("min of range: " + data[2])
					print("max of range: " + data[3])
				if data[4] != "NA":
					inputlist = data[4]
					strlist = list(inputlist)
					for x in range(len(strlist)):
						if strlist[x] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
							timeslist.append(math.floor(float(strlist[x])))
					print("list: " + data[4])
				mode = data[5]
				print("mode: " + data[5])

		# don't read from existing configuration
		else:
			interval = math.floor(float(entrylist[2].get())) # the value get from GUI window, need to be converted into floating number
			duration = math.floor(float(entrylist[3].get()))
			if entrylist[4].get() != "": # if user enter the value in range
				rangemin = math.floor(float(entrylist[4].get()))
				rangemax = math.floor(float(entrylist[5].get()))
			else: # otherwise, save as None
				rangemin = "NA"
				rangemax = "NA"
			if entrylist[6].get() != "": # if user enter the value in list
				inputlist = entrylist[6].get()
				strlist = inputlist.split(" ")
				for x in range(len(strlist)):
						timeslist.append(math.floor(float(strlist[x])))
			else:
				inputlist = "NA"
			mode = entrylist[7].get()
			with open('configuration_variable.csv', 'w', newline='') as f: # save parameters
				w = csv.writer(f)
				w.writerow(["Interval between two times", "Duration of feeding", "Min of range", "Max of range", "Input list", "mode"])
				data = [interval, duration, rangemin, rangemax, timeslist, mode]
				w.writerow(data)
		paralist = [interval,duration,rangemin,rangemax,timeslist,mode,currenttimes,upanddown]
		unparalist = [currenttimes,upanddown,trialtimes,timelength]
		para = open(str(systemlist[3]), 'a', newline='')
		para.write("interval: " + str(interval) + "\n")
		para.write("duration: " + str(duration) + "\n")
		para.write("rangemin: " + str(rangemin) + "\n")
		para.write("rangemax: " + str(rangemax) + "\n")
		para.write("timeslist: " + str(timeslist) + "\n")
		para.write("mode: " + str(mode) + "\n")
		para.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		# call the function that contains the sub-function	
		run(systemlist,paralist,unparalist,pinlist)

def run(systemlist,paralist,unparalist,pinlist):
	thistimes = 0
	
	# range mode, then call the main body for this mode
	if paralist[5] == "R":
		thistimes = random.randint(paralist[2], paralist[3]) # initial the criterion for each trial
		print("This time is " + str(thistimes))
		paralist.append(thistimes)
		rangemode(systemlist,paralist,unparalist,pinlist)

	# list mode
	elif paralist[5] == "L":
		thistimes=random.choice(paralist[4])
		print("This time is " + str(thistimes))
		paralist.append(thistimes)
		listmode(systemlist,paralist,unparalist,pinlist)


def rangemode(systemlist,paralist,unparalist,pinlist):
	if unparalist[2] == 0 or time.time() - systemlist[2] >= unparalist[3]:
		exit(systemlist[0], systemlist[1])
	unparalist[0],unparalist[1] = arduino.monitor(paralist[8], unparalist[0], unparalist[1], systemlist[2], systemlist[3], pinlist[0], pinlist[1], systemlist[1],systemlist[4])
	if unparalist[0] == paralist[8]:
		#record the time that it achieves the criterion
		arduino.recordtime(systemlist[2], systemlist[3], "E")
		arduino.delay(paralist[0],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
		unparalist[0] = arduino.us(paralist[1],pinlist[2],pinlist[0],systemlist[2],systemlist[3],systemlist[0],systemlist[1])
		paralist[8] = random.randint(paralist[2], paralist[3]) # select another criterion for new trial
		print("This time is " + str(paralist[8]))
		unparalist[2] -= 1
		print("times to go: " + str(unparalist[2]))
		print("time already pass: " + str(time.time() - systemlist[2]))
	# recall itself every 1milisecond in order to keep monitoring the press
	systemlist[1].after(1,rangemode,systemlist,paralist,unparalist,pinlist)

# listmode is similar to range
def listmode(systemlist,paralist,unparalist,pinlist):
	if unparalist[2] == 0 or time.time() - systemlist[2] >= unparalist[3]:
		exit(systemlist[0], systemlist[1])
	unparalist[0],unparalist[1] = arduino.monitor(paralist[8], unparalist[0], unparalist[1], systemlist[2], systemlist[3], pinlist[0], pinlist[1], systemlist[1],systemlist[4])
	# feed
	if unparalist[0] == paralist[8]:
		#record the time that it achieves the criterion
		arduino.recordtime(systemlist[2], systemlist[3], "E")
		arduino.delay(paralist[0],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
		unparalist[0] = arduino.us(paralist[1],pinlist[2],pinlist[0],systemlist[2],systemlist[3],systemlist[0],systemlist[1])
		paralist[8]=random.choice(paralist[4])
		print("This time is " + str(paralist[8]))
		unparalist[2] -= 1
		print("times to go: " + str(unparalist[2]))
		print("time already pass: " + str(time.time() - systemlist[2]))
	systemlist[1].after(1,listmode,systemlist,paralist,unparalist,pinlist)

# exit button function
def exit(board,top):
	board.exit()
	top.destroy()


if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])