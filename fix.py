"""
 Fixed ratio operant conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting reward 
 according to whether the rat has achieved the criterion

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
import arduino



def main(port,output,num):
	portname = 'COM' + str(port)
	board = pyfirmata.Arduino(portname)

	if output == "N":
		now = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
		output = "output_fix_" + str(now) + ".txt"

	open(output, 'w').close()
	title = open(str(output), 'a', newline='')
	title.write("Arduino " + str(num) + " Fixed Ratio" + "\n")
	title.close()

	# Using iterator thread to avoid buffer overflow
	it = pyfirmata.util.Iterator(board)
	it.start()

	# Define pins and select corresponding modes
	operantPin = board.get_pin('d:3:i')
	csPin = board.get_pin('d:11:o')
	usPin = 13
	board.digital[usPin].mode = pyfirmata.SERVO

	# start time of the experiment
	starttime = time.time()

	# Initialize main windows with title and size
	top = tkinter.Tk()
	top.title("Arduino " + str(num) + " Fix Ratio")

	tkinter.Label(top, text = "Pretest: Y/N").grid(column = 1, row = 1)
	preEntry = tkinter.Entry(top)
	preEntry.grid(column=2, row=1) # to manage the location on window
	preEntry.focus_set()

	tkinter.Label(top, text = "Load: Y/N").grid(column = 1, row = 2)
	loadEntry = tkinter.Entry(top)
	loadEntry.grid(column = 2, row = 2)
	loadEntry.focus_set()

	# get parameters

	# how many times press = reward
	tkinter.Label(top, text = "Times: ").grid(column = 1, row = 3)
	timesEntry = tkinter.Entry(top)
	timesEntry.grid(column = 2, row = 3)
	timesEntry.focus_set()

	# the interval between each time
	tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 4)
	intervalEntry = tkinter.Entry(top)
	intervalEntry.grid(column = 2, row = 4)
	intervalEntry.focus_set()

	# how long will the feeding last
	tkinter.Label(top, text = "Duration: ").grid(column = 1, row = 5)
	durationEntry = tkinter.Entry(top)
	durationEntry.grid(column = 2, row = 5)
	durationEntry.focus_set()

	tkinter.Label(top, text = "trial times: ").grid(column = 1, row = 6)
	trialEntry = tkinter.Entry(top)
	trialEntry.grid(column = 2, row = 6)
	tkinter.Label(top, text = "times").grid(column = 3, row = 6)

	tkinter.Label(top, text = "length: ").grid(column = 1, row = 7)
	lengthEntry = tkinter.Entry(top)
	lengthEntry.grid(column = 2, row = 7)
	tkinter.Label(top, text = "hours").grid(column = 3, row = 7)

	systemlist = [board,top,starttime,output,num]
	entrylist = [preEntry,loadEntry,timesEntry,intervalEntry,durationEntry,trialEntry,lengthEntry]
	pinlist = [operantPin,csPin,usPin]

	# Create Start and Exit button

	# button for main function
	startButton = tkinter.Button(top, text="Start", command=lambda: pressbutton(systemlist,entrylist,pinlist,startButton))
	startButton.grid(column=1, row=8)

	# exit button
	exitButton = tkinter.Button(top, text="Exit", command=lambda: exit(board,top))
	exitButton.grid(column=2, row=8)


	# Start and open the window
	top.mainloop()


def pressbutton(systemlist,entrylist,pinlist,startButton):
	currenttimes = 0 # the times that the rat already press
	upanddown = 0 # save the status of button

	trialtimes = math.inf
	timelength = math.inf

	if entrylist[5].get() != "": # trial mode
		trialtimes = int(entrylist[5].get())
	if entrylist[6].get() != "":
		timelength = float(entrylist[6].get()) * 3600 # change to second

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
			with open('configuration_fix.csv', 'r', newline='') as f:
				r = csv.reader(f)
				data = None
				count = 0
				for row in r:
					if count == 1:
						data = row
					count += 1
				times = float(data[0])
				interval = float(data[1])
				duration= float(data[2])
				print("read result: ")
				print("times: " + data[0])
				print("interval: " + data[1])
				print("duration: " + data[2])

		# don't read from existing configuration
		else:
			times = float(entrylist[2].get()) # the value get from GUI window, need to be converted into floating number
			interval = float(entrylist[3].get())
			duration = float(entrylist[4].get())
			with open('configuration_fix.csv', 'w', newline='') as f: # save parameters
				w = csv.writer(f)
				w.writerow(["Number of times", "Interval between two times", "Duration of feeding"])
				data = [times, interval, duration]
				w.writerow(data)
		paralist = [times,interval,duration]
		unparalist = [currenttimes,upanddown,trialtimes,timelength]
		para = open(str(systemlist[3]), 'a', newline='')
		para.write("times: " + str(times) + "\n")
		para.write("interval: " + str(interval) + "\n")
		para.write("duration: " + str(duration) + "\n")
		para.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		# call the function that contains the main body
		run(systemlist,paralist,unparalist,pinlist)

def run(systemlist,paralist,unparalist,pinlist):
	if unparalist[2] == 0 or time.time() - systemlist[2] >= unparalist[3]:
		exit(systemlist[0], systemlist[1])
	unparalist[0],unparalist[1] = arduino.monitor(paralist[0], unparalist[0], unparalist[1], systemlist[2], systemlist[3], pinlist[0], pinlist[1], systemlist[1],systemlist[4])
	if unparalist[0] == paralist[0]:
		arduino.recordtime(systemlist[2], systemlist[3], "E")
		arduino.delay(paralist[1],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
		unparalist[0] = arduino.us(paralist[2],pinlist[2],pinlist[0],systemlist[2],systemlist[3],systemlist[0],systemlist[1])
		unparalist[2] -= 1
		print("times to go: " + str(unparalist[2]))
		print("time already pass: " + str(time.time() - systemlist[2]))
	# recall itself every 1milisecond in order to keep monitoring the press
	systemlist[1].after(1,run,systemlist,paralist,unparalist,pinlist)


# exit button function
def exit(board,top):
	board.exit()
	top.destroy()

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])
