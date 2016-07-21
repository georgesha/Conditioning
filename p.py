	
"""
 Progressive ratio operant conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting reward 
 according to whether the rat has achieved the criterion
 where the criterion increases every certain trials

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
from random import randint # to randomly select from a range or a list
import arduino

def main(port,output,num):
	portname = 'COM' + str(port)
	board = pyfirmata.Arduino(portname)

	if output == "N":
		now = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
		output = "output_prograssive_" + str(now) + ".txt"

	open(output, 'w').close()
	title = open(str(output), 'a', newline='')
	title.write("Arduino " + str(num) + " Prograssive Ratio" + "\n")
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
	top.title("Arduino " + str(num) + " P Ratio")

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
	tkinter.Label(top, text = "starting criterion: ").grid(column = 1, row = 3)
	timesEntry = tkinter.Entry(top)
	timesEntry.grid(column = 2, row = 3)
	timesEntry.focus_set()
	tkinter.Label(top,text="presses").grid(column=3, row=3)


	# the interval between completing of pressing and feeding food
	tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 4)
	intervalEntry = tkinter.Entry(top)
	intervalEntry.grid(column = 2, row = 4)
	intervalEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=4)


	# how long will the feeding last
	tkinter.Label(top, text = "Duration of food: ").grid(column = 1, row = 5)
	durationEntry = tkinter.Entry(top)
	durationEntry.grid(column = 2, row = 5)
	durationEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=5)

	# how many presses to increase as progressive ratio
	tkinter.Label(top,text="increasing step:").grid(column=1, row=6)
	stepEntry = tkinter.Entry(top)
	stepEntry.grid(column=2, row=6)
	tkinter.Label(top, text = "Random: Y/N").grid(column = 3, row = 6)
	randomEntry = tkinter.Entry(top)
	randomEntry.grid(column = 4, row = 6)
	randomEntry.focus_set()

	# every how many trials does the criterion increase  
	tkinter.Label(top,text="trial interval of each increment:").grid(column=1, row=7)
	gapEntry = tkinter.Entry(top)
	gapEntry.grid(column=2, row=7)
	tkinter.Label(top,text="times").grid(column=3, row=7)

	tkinter.Label(top, text = "trial times: ").grid(column = 1, row = 8)
	trialEntry = tkinter.Entry(top)
	trialEntry.grid(column = 2, row = 8)
	tkinter.Label(top, text = "times").grid(column = 3, row = 8)

	tkinter.Label(top, text = "length: ").grid(column = 1, row = 9)
	lengthEntry = tkinter.Entry(top)
	lengthEntry.grid(column = 2, row = 9)
	tkinter.Label(top, text = "hours").grid(column = 3, row = 9)
	
	systemlist = [board,top,starttime,output,num]
	entrylist = [preEntry,loadEntry,timesEntry,intervalEntry,durationEntry,stepEntry,randomEntry,gapEntry,trialEntry,lengthEntry]
	pinlist = [operantPin,csPin,usPin]

	# Create Start and Exit button

	# button for main function
	startButton = tkinter.Button(top, text="Start", command=lambda: pressbutton(systemlist,entrylist,pinlist,startButton))
	startButton.grid(column=2, row=10)

	# exit button
	exitButton = tkinter.Button(top, text="Exit", command=lambda: exit(board,top))
	exitButton.grid(column=3, row=10)

	top.mainloop()


# main function
def pressbutton(systemlist,entrylist,pinlist,startButton):

	currenttimes = 0 # create a variable to count the presses that lead to reward
	totaltimes = 0 # create a variable to count the total trials the rat has completed used to decide the increment
	upanddown = 0

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
		# let the user to press once to check button's function
		print ('please press the button once')
		currenttimes = 0
		upanddown = 0
		while True:
			if pinlist[0].read() == 1: # if button is pressed, .read() will return 1
				if upanddown == 0:
					upanddown = 1
					pinlist[1].write(1)
					systemlist[1].update()
					sleep(0.1)
					pinlist[1].write(0) # make the LED blink once to indicate the press lead to reward
					currenttimes += 1
					
					# if one press is detected, deliver the food
					if currenttimes == 1:
						print ('press completed')
						systemlist[1].update()			
						sleep(1)
						print ('start feeding')
						arduino.food("deliver",systemlist[0],pinlist[2],systemlist[1])
						print ('stay feeding')
						sleep(2)
						print ('feeding end')
						arduino.food("remove",systemlist[0],pinlist[2],systemlist[1])
						currenttimes = 0 # reset for a new trail				 
			if upanddown == 1:
				if pinlist[0].read() == 0:
					upanddown = 0	
	# implement the experiment	
	else:
		# whether load the configuration
		# read from existing configuration and print them out
		if entrylist[1].get() == "Y":
			with open('configuration_p.csv', 'r', newline="") as f:
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
				if data[3]=='random':
					step = data[3]
				else:
					step = int(data[3])
				gap = int(data[4])
				print("times: " + data[0])
				print("interval: " + data[1])
				print("duration: " + data[2])
				print("step: " + data[3])
				print("gap: " + data[4])
				
		# don't read from existing configuration
		else:
			times = float(entrylist[2].get()) # the value get from GUI window, need to be converted into floating number
			interval = float(entrylist[3].get())
			duration = float(entrylist[4].get())
			if entrylist[6].get() == "Y":
				step="random"
			else:
				step=int(entrylist[5].get())
			gap = int(entrylist[7].get())
			with open('configuration_p.csv', 'w', newline="") as f: # save parameters
				w = csv.writer(f)
				w.writerow(["Number of press", "Interval between press and feed", "Duration of feeding","Incresing step","Trials between increment"])
				data = [times,interval,duration,step,gap]
				w.writerow(data)

	paralist = [times,interval,duration,step,gap,currenttimes,upanddown,totaltimes]
	unparalist = [currenttimes,upanddown,totaltimes,trialtimes,timelength]
	para = open(str(systemlist[3]), 'a', newline='')
	para.write("times: " + str(times) + "\n")
	para.write("interval: " + str(interval) + "\n")
	para.write("duration: " + str(duration) + "\n")
	para.write("step: " + str(step) + "\n")
	para.write("gap: " + str(gap) + "\n")
	# call the function that contains the main body
	run(systemlist,paralist,unparalist,pinlist)

def run(systemlist,paralist,unparalist,pinlist):
	if unparalist[3] == 0 or time.time() - systemlist[2] >= unparalist[4]:
		exit(systemlist[0], systemlist[1])
	unparalist[0],unparalist[1] = arduino.monitor(paralist[0], unparalist[0], unparalist[1], systemlist[2], systemlist[3], pinlist[0], pinlist[1], systemlist[1],systemlist[4])
	# if the rat achieve the criterion, that actions according to the time sequence
	# during this section, all actions and presses that do not lead to reward are recorded to file as well
	if unparalist[0] == paralist[0]:
		arduino.recordtime(systemlist[2], systemlist[3], "E")
		arduino.delay(paralist[1],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
		#record the time that it achieves the criterion				
		unparalist[0] = arduino.us(paralist[2],pinlist[2],pinlist[0],systemlist[2],systemlist[3],systemlist[0],systemlist[1])
		
		# for every certain trails, the criterion need to be increased
		# the trails that increase the criterion is the number that dividable by 'gap'
		if unparalist[2] % paralist[4]==0:
			if paralist[3]=="random":
				s=randint(1,3) # if user select random as step, randomly select it from one to three
				print (s) # and print this step out
				paralist[0] += s
			else:
				paralist[0] += paralist[3]
		unparalist[3] -= 1
		print("current times is: " + str(paralist[0])) # print the current criterion out
		print("times to go: " + str(unparalist[3]))
		print("time already pass: " + str(time.time() - systemlist[2]))
	# recall itself every 1milisecond in order to keep monitoring the press	 
	systemlist[1].after(1,run,systemlist,paralist,unparalist,pinlist)


# exit button function
def exit(board,top):
	board.exit()
	top.destroy()

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])