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
import math # help do calculation when getting ralative time
import random # random select the criterion for each trial
import arduino


def main(port,output):

	portname = 'COM' + str(port)
	board = pyfirmata.Arduino(portname)

	# Using iterator thread to avoid buffer overflow
	it = pyfirmata.util.Iterator(board)
	it.start()

	# Define pins
	buttonPin = board.get_pin('d:3:i')
	LEDPin = board.get_pin('d:11:o')
	servoPin = 13
	board.digital[servoPin].mode = pyfirmata.SERVO

	# start time of the experiment
	starttime = time.time()

	# open the file and save actions during experiment
	if output == "N":
		output = open('output_v.txt', 'w', newline='')
	else:
		output = open(str(output), 'w', newline='')


	# Initialize main windows with title and size
	top = tkinter.Tk()
	top.title("Variable Ratio")

	#create the checkbox for pre-test
	tkinter.Label(top, text = "Pretest: Y/N").grid(column = 1, row = 1)
	preEntry = tkinter.Entry(top)
	preEntry.grid(column=2, row=1) # to manage the location on window
	preEntry.focus_set()

	tkinter.Label(top, text = "Load: Y/N").grid(column = 1, row = 2)
	loadEntry = tkinter.Entry(top)
	loadEntry.grid(column = 2, row = 2)
	loadEntry.focus_set()

	# create the checkbox for range or List
	tkinter.Label(top, text = "Mode: L/R").grid(column = 1, row = 8)
	modeEntry = tkinter.Entry(top)
	modeEntry.grid(column = 2, row = 8)
	modeEntry.focus_set()

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


	# Create Start and Exit button

	# button for main function
	startButton = tkinter.Button(top, text="Start", command=lambda: pressbutton(starttime,board,top,startButton,preEntry,loadEntry,modeEntry,intervalEntry,durationEntry,rangeminEntry,rangemaxEntry,listEntry,output,buttonPin,LEDPin,servoPin))
	startButton.grid(column=1, row=7)

	# exit button
	exitButton = tkinter.Button(top, text="Exit", command=lambda: exit(board,top))
	exitButton.grid(column=2, row=7)

	#start and open the window
	top.mainloop()

# main function
def pressbutton(starttime,board,top,startButton,preEntry,loadEntry,modeEntry,intervalEntry,durationEntry,rangeminEntry,rangemaxEntry,listEntry,output,buttonPin,LEDPin,servoPin):
	# create a variable to achieve correct detection of the state of button
	# it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
	# and it will be changed to zero again only when the button is released
	# after it back to zero, another press will be detected and count as active press
	# meanwhile, this variable can count for the rising and falling edge of button	
	
	upanddown = 0
	currenttimes = 0 # the times that the rat already press
	timeslist = []
	rangemin = 0
	rangemax = 0
	# disable the start button to avoid double-click during executing
	startButton.config(state=tkinter.DISABLED)
	
	# If user choose to pre-test
	# automatically start a trial that implement all the hardware
	# in order to check basic settings	
	if preEntry.get() == "Y":
		# get a list to test
		l=input("please enter a list of presses:")
		# convert into list
		strlist = list(l)
		# get the siginificant value in the list and save them into a new list
		# the number in this list is the range that the criterion can be selected from
		for x in range(len(strlist)):
			if strlist[x] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
				timeslist.append(math.floor(float(strlist[x])))
		# randomly select the criterion for each trial
		thistimes=random.choice(timeslist)
		# print it out
		print(thistimes)
		while True:
			if buttonPin.read() == 1: # if button is pressed, .read() will return 1
				if upanddown == 0:
					upanddown = 1
					LEDPin.write(1)
					top.update()
					sleep(0.1)
					LEDPin.write(0) # make the LED blink once to indicate the press lead to reward
					currenttimes += 1; # count it into presses that lead to reward
					# feed
					if currenttimes == thistimes:
						print ('press completed')
						top.update()
						sleep(1)
						print ('start feeding')
						arduino.food("deliver",board,servoPin,top)
						print ('stay feeding')
						sleep(2)
						print ('feeding end')
						arduino.food("remove",board,servoPin,top)
						currenttimes = 0 # reset currenttimes for new trials
				if upanddown == 1:
					if buttonPin.read() == 0:
						upanddown = 0 
						
	# implement the experiment						
	else:
		# whether load the configuration
		# read from existing configuration and print them out
		if loadEntry.get() == "Y":
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
			interval = math.floor(float(intervalEntry.get())) # the value get from GUI window, need to be converted into floating number
			duration = math.floor(float(durationEntry.get()))
			if rangeminEntry.get() != "": # if user enter the value in range
				rangemin = math.floor(float(rangeminEntry.get()))
				rangemax = math.floor(float(rangemaxEntry.get()))
			else: # otherwise, save as None
				rangemin = "NA"
				rangemax = "NA"
			if listEntry.get() != "": # if user enter the value in list
				inputlist = listEntry.get()
				strlist = inputlist.split(" ")
				for x in range(len(strlist)):
						timeslist.append(math.floor(float(strlist[x])))
			else:
				inputlist = "NA"
			mode = modeEntry.get()
			with open('configuration_variable.csv', 'w', newline='') as f: # save parameters
				w = csv.writer(f)
				w.writerow(["Interval between two times", "Duration of feeding", "Min of range", "Max of range", "Input list", "mode"])
				data = [interval, duration, rangemin, rangemax, timeslist, mode]
				w.writerow(data)
	
	# call the function that contains the sub-function	
	run(starttime,board,top,interval,duration,rangemin,rangemax,timeslist,mode,currenttimes,upanddown,output,buttonPin,LEDPin,servoPin)

def run(starttime,board,top,interval,duration,rangemin,rangemax,timeslist,mode,currenttimes,upanddown,output,buttonPin,LEDPin,servoPin):
	thistimes = 0
	
	# range mode, then call the main body for this mode
	if mode == "R":
		thistimes = random.randint(rangemin, rangemax) # initial the criterion for each trial
		print(thistimes)
		rangemode(starttime,board,top,interval,duration,rangemin,rangemax,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin)

	# list mode
	elif mode == "L":
		thistimes=random.choice(timeslist)
		print(thistimes)
		listmode(starttime,board,top,interval,duration,timeslist,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin)


def rangemode(starttime,board,top,interval,duration,rangemin,rangemax,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin):
	currenttimes,upanddown = arduino.monitor(thistimes, currenttimes, upanddown, starttime, output, buttonPin, LEDPin, top)
	if currenttimes == thistimes:
		#record the time that it achieves the criterion
		arduino.recordtime(starttime, output, "E")
		arduino.delay(interval,starttime,buttonPin,output,board,top)
		currenttimes = arduino.us(duration,servoPin,buttonPin,starttime,output,board,top)
		thistimes = random.randint(rangemin, rangemax) # select another criterion for new trial
		print(thistimes)

	# recall itself every 1milisecond in order to keep monitoring the press
	top.after(1,rangemode,starttime,board,top,interval,duration,rangemin,rangemax,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin)

# listmode is similar to range
def listmode(starttime,board,top,interval,duration,timeslist,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin):
	currenttimes,upanddown = arduino.monitor(thistimes,currenttimes,upanddown,starttime,output,buttonPin,LEDPin,top) 
	# feed
	if currenttimes == thistimes:
		arduino.recordtime(starttime, output, "E")
		arduino.delay(interval,starttime,buttonPin,output,board,top)
		currenttimes = arduino.us(duration,servoPin,buttonPin,starttime,output,board,top)
		thistimes=random.choice(timeslist)
		print(thistimes)
			
	top.after(1,listmode,starttime,board,top,interval,duration,timeslist,currenttimes,upanddown,thistimes,output,buttonPin,LEDPin,servoPin)

# exit button function
def exit(board,top):
	board.exit()
	top.destroy()


if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2])