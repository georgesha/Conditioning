	
"""
 Classical conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting CS and US 
 according to these sequences and entries 

 The circuit:
 * Red LED attached from pin 11 to +5V
 * Green LED attached from pin 12 to +5V 
 * 560 Ohm resistors attached from pin 11&12 to GND
 * Servo attached to pin 13

 """


# Import all needed libraries
import tkinter # GUI window
from time import sleep # delay to achieve time sequence
import pyfirmata # Arduino Uno board
import csv # saving information to files
import random # randomly choose the interval
import time
import datetime
import math
import sys # correctly shut down the program
import arduino


def main(port,output,num):
	portname = 'COM' + str(port)
	board = pyfirmata.Arduino(portname)

	# Define pins
	greenPin = board.get_pin('d:11:o')
	redPin = board.get_pin('d:12:o')
	servoPin = 13
	board.digital[servoPin].mode = pyfirmata.SERVO

	# Initialize main windows with title and size
	top = tkinter.Tk()
	top.title("Arduino " + str(num) +  " classical")

	# start time of the experiment
	starttime = time.time()

	tkinter.Label(top, text = "Pretest: Y/N").grid(column = 1, row = 1)
	preEntry = tkinter.Entry(top)
	preEntry.grid(column=2, row=1) # to manage the location on window
	preEntry.focus_set()

	tkinter.Label(top, text = "Load: Y/N").grid(column = 1, row = 2)
	loadEntry = tkinter.Entry(top)
	loadEntry.grid(column = 2, row = 2)
	loadEntry.focus_set()

	#get parameters
	 
	#cs
	tkinter.Label(top,text="cs duration: ").grid(column=1, row=3)
	csEntry = tkinter.Entry(top)
	csEntry.grid(column=2, row=3)
	csEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=3)

	#us 
	tkinter.Label(top,text="us duration: ").grid(column=1, row=4)
	usEntry = tkinter.Entry(top)
	usEntry.grid(column=2, row=4)
	usEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=4)

	#between cs&us
	tkinter.Label(top,text="interval between cs&us: ").grid(column=1, row=5)
	betweenEntry = tkinter.Entry(top)
	betweenEntry.grid(column=2, row=5)
	betweenEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=5)

	tkinter.Label(top,text="(negative interval means overlap)").grid(column=2, row=6)

	#intertrial
	tkinter.Label(top,text="intertrial interval: ").grid(column=1, row=7)
	intertrialEntry = tkinter.Entry(top)
	intertrialEntry.grid(column=2, row=7)
	intertrialEntry.focus_set()
	tkinter.Label(top,text="seconds").grid(column=3, row=7)
	#whether intertrial interval is random

	tkinter.Label(top, text = "Random: Y/N").grid(column = 4, row = 7)	
	randomEntry = tkinter.Entry(top)
	randomEntry.grid(column = 5, row = 7)
	randomEntry.focus_set()	

	#create the checkbox for conditioned stimulus
	tkinter.Label(top,text="conditioned stimulus: ").grid(column=1, row=8)
	#green or red
	LEDEntry = tkinter.Entry(top)
	LEDEntry.grid(column = 2, row = 8)
	LEDEntry.focus_set()
	tkinter.Label(top, text = "LED: G/R").grid(column = 3, row = 8)
	

	# Create checkbox for different conditioning modes

	tkinter.Label(top,text="conditioning mode: ").grid(column=1, row=9)
	#3 conditioning
	modeEntry = tkinter.Entry(top)
	modeEntry.grid(column = 2, row = 9)
	modeEntry.focus_set()
	tkinter.Label(top, text = "F/T/B").grid(column = 3, row = 9)	

	tkinter.Label(top, text = "trial times: ").grid(column = 1, row = 11)
	trialEntry = tkinter.Entry(top)
	trialEntry.grid(column = 2, row = 11)
	tkinter.Label(top, text = "times").grid(column = 3, row = 11)

	tkinter.Label(top, text = "length: ").grid(column = 1, row = 12)
	lengthEntry = tkinter.Entry(top)
	lengthEntry.grid(column = 2, row = 12)
	tkinter.Label(top, text = "hours").grid(column = 3, row = 12)

	systemlist = [board,top,starttime]
	entrylist = [preEntry,loadEntry,csEntry,usEntry,betweenEntry,intertrialEntry,randomEntry,LEDEntry,modeEntry,trialEntry,lengthEntry]
	pinlist = [greenPin,redPin,servoPin]

	# Create Start and Exit button

	startButton = tkinter.Button(top,text="Start",command=lambda: pressbutton(systemlist,entrylist,pinlist,startButton))# call the function of start button
	startButton.grid(column=2, row=13)

	exitButton = tkinter.Button(top,text="Exit",command=lambda: exit(board,top))# call the function of exit button
	exitButton.grid(column=3, row=13)

	# Start and open the window
	top.mainloop()


#function for start button
def pressbutton(systemlist,entrylist,pinlist,startButton):
	# disable the start button to avoid double-click during executing
	startButton.config(state=tkinter.DISABLED)

	trialtimes = math.inf
	timelength = math.inf

	if entrylist[9].get() != "": # trial mode
		trialtimes = int(entrylist[9].get())
	if entrylist[10].get() != "":
		timelength = float(entrylist[10].get()) * 3600 # change to second

	# If user choose to pre-test
	# automatically start a trial that implement all the hardware
	# in order to check basic settings
	if entrylist[0].get() == "Y": # if the box for pre-test is checked, it .get() will return '1'
		# assign simple paramters for pre-test
		inputlist = []
		outputlist = [pinlist[0],pinlist[1],pinlist[2]]
		arduino.pretest(systemlist[0], systemlist[1], inputlist, outputlist)		
		
	# implement the experiment
	else:
		# whether load the configuration
		# if load, assign parameters from file and print them out
		if entrylist[1].get() == "Y":
			with open('configuration_cc.csv', 'r', newline="") as f:
				r = csv.reader(f)
				data = None
				count = 0
				for row in r: # loop to read from the file
					if count == 1:
						data = row
					count += 1
				dur_c = float(data[0])
				dur_u = float(data[1])
				btw = float(data[2])
				if data[3]=="random":
					inter = data[3]
				else:
					inter = float(data[3])
				red = data[4]
				green = data[5]
				mode = data[6]
				print("read result: ")
				print("conditioned duration: " + str(dur_c))
				print("unconditioned duration: " + str(dur_u))
				print("interval between CS&US: " + str(btw))
				print("intertrial interval: " + str(inter))
				print("mode: " + str(mode))
		# if not load, get parameters from entries
		# and save them to the configuration files
		else:
			dur_c = float(entrylist[2].get())
			dur_u = float(entrylist[3].get())
			btw = float(entrylist[4].get())
			if entrylist[6].get() == "Y":
				inter = "random"
			else:
				inter = float(entrylist[5].get())
			if entrylist[7].get() == "R":
				red = 1
				green = 0
			else:
				red = 0
				green = 1
			if entrylist[7].get() == "G":
				green = 1
				red = 0
			else:
				green = 0
				red = 1
			mode = entrylist[8].get()
			with open('configuration_cc.csv', 'w', newline="") as f: # save parameters
				w = csv.writer(f)
				w.writerow(["CS duration", "US duration", "interval between CS and US", "intertrial interval","red LED","green LED","MODE"])
				data = [dur_c, dur_u, btw, inter,red,green,mode]
				w.writerow(data) 
		
		paralist = [dur_c, dur_u, btw, inter,red,green]
		unparalist = [trialtimes,timelength]
		# check the choice for mode and call corresponding function
		if mode=="F":
			forward(systemlist,paralist,unparalist,pinlist)
		elif mode=="T":
			temporal(systemlist,paralist,unparalist,pinlist)
		elif mode=="B":
			blocking(systemlist,paralist,unparalist,pinlist)
	
# define the function of exit
def exit(board,top):
	board.exit()
	top.destroy()


#forward
def forward (systemlist,paralist,unparalist,pinlist):
	if unparalist[0] == 0 or time.time() - systemlist[2] >= unparalist[1]:
		exit(systemlist[0], systemlist[1])

	# if there is no overlap between CS and US
	if paralist[2]>=0:
		# turn on CS
		arduino.cs(pinlist[0],paralist[4])
		arduino.cs(pinlist[1],paralist[5])
		# delay for the duration of CS
		arduino.c_delay(paralist[0],systemlist[1])
		# turn off CS
		arduino.cs(pinlist[0],0)
		arduino.cs(pinlist[1],0)	
		# delay for the interval between CS and US
		arduino.c_delay(paralist[2],systemlist[1])
		# deliver food
		arduino.c_food("delive",systemlist[0],pinlist[2],systemlist[1])
		# delay for the duration of US
		arduino.c_delay(paralist[1],systemlist[1])
		# remove food
		arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
		# delay for the paralist[3]-trial interval
		arduino.c_delay(paralist[3],systemlist[1])
		unparalist[0] -= 1
		# if the amount has not matched the requirement, call the function for this mode again
		forward (systemlist,paralist,unparalist,pinlist)
			
	# if there is overlap between CS and US
	else:
		# If CS is gone before US
		if -1*paralist[2]<=paralist[1]: # -1 due to the negative value for overlap
			# turn on CS
			arduino.cs(pinlist[0],paralist[4])
			arduino.cs(pinlist[1],paralist[5])
			# delay for the time until US is supposed to present
			arduino.c_delay(paralist[0]+paralist[2],systemlist[1])
			# deliver food
			arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
			# delay for the time until the overlap of CS has passed,
			# i.e., the interval between CS and US
			arduino.c_delay(-1*paralist[2],systemlist[1])
			# turn off CS
			arduino.cs(pinlist[0],0)
			arduino.cs(pinlist[1],0)
			# delay for the time until the duration of it has been fulfilled
			arduino.c_delay(paralist[2]+paralist[1],systemlist[1])
			# remove food
			arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
			# delay for the paralist[3]-trial interval
			arduino.c_delay(paralist[3],systemlist[1])
			unparalist[0] -= 1
			# if the amount has not matched the requirement, call the function for this mode again
			forward (systemlist,paralist,unparalist,pinlist)
		
		# cs is gone after us
		else: 
			# turn on CS
			arduino.cs(pinlist[0],paralist[4])
			arduino.cs(pinlist[1],paralist[5])
			# delay until US is supposed to present
			arduino.c_delay(paralist[0]+paralist[2],systemlist[1])
			# deliver food
			arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
			# delay for the duration of US
			arduino.c_delay(paralist[1],systemlist[1])
			# remove food
			arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
			# delay until fulfill the duration of CS
			arduino.c_delay(paralist[0]+paralist[2]-paralist[1],systemlist[1])
			# turn off CS
			arduino.cs(pinlist[0],0)
			arduino.cs(pinlist[1],0)
			# delay for the paralist[3]-trial interval
			arduino.c_delay(paralist[3],systemlist[1])
			unparalist[0] -= 1
			# if the amount has not matched the requirement, call the function for this mode again
			forward (systemlist,paralist,unparalist,pinlist)
				
#temporal
def temporal(systemlist,paralist,unparalist,pinlist):
	if unparalist[0] == 0 or time.time() - systemlist[2] >= unparalist[1]:
		exit(systemlist[0], systemlist[1])
	# deliver food
	arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
	# delay for the duration of US
	arduino.c_delay(paralist[1],systemlist[1])
	# remove food
	arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
	# delay for the paralist[3]-trial interval
	arduino.c_delay(paralist[3],systemlist[1])
	unparalist[0] -= 1	
	# if the amount has not matched the requirement, call the function for this mode again
	temporal(systemlist,paralist,unparalist,pinlist)
		
#blocking
# this mode is similar to forward, except that it uses both red and green LEDs
def blocking(systemlist,paralist,unparalist,pinlist):
	if unparalist[0] == 0 or time.time() - systemlist[2] >= unparalist[1]:
		exit(systemlist[0], systemlist[1])
	# if there is no overlap between CS and US
	if paralist[2]>=0:
		# turn on CS
		arduino.cs(pinlist[0],1)
		arduino.cs(pinlist[1],1)
		# delay for the duration of CS
		arduino.c_delay(paralist[0],systemlist[1])
		# turn off CS
		arduino.cs(pinlist[0],0)
		arduino.cs(pinlist[1],0)	
		# delay for the interval between CS and US
		arduino.c_delay(paralist[2],systemlist[1])
		# deliver food
		arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
		# delay for the duration of US
		arduino.c_delay(paralist[1],systemlist[1])
		# remove food
		arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
		# delay for the paralist[3]-trial interval
		arduino.c_delay(paralist[3],systemlist[1])
		unparalist[0] -= 1
		# if the amount has not matched the requirement, call the function for this mode again
		blocking (systemlist,paralist,unparalist,pinlist)
			
	# if there is overlap between CS and US
	else:
		# If CS is gone before US
		if -1*paralist[2]<=paralist[1]: # -1 due to the negative value for overlap
			# turn on CS
			arduino.cs(pinlist[0],1)
			arduino.cs(pinlist[1],1)
			# delay for the time until US is supposed to present
			arduino.c_delay(paralist[0]+paralist[2],systemlist[1])
			# deliver food
			arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
			# delay for the time until the overlap of CS has passed,
			# i.e., the interval between CS and US
			arduino.c_delay(-1*paralist[2],systemlist[1])
			# turn off CS
			arduino.cs(pinlist[0],0)
			arduino.cs(pinlist[1],0)
			# delay for the time until the duration of it has been fulfilled
			arduino.c_delay(paralist[2]+paralist[1],systemlist[1])
			# remove food
			arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
			# delay for the paralist[3]-trial interval
			arduino.c_delay(paralist[3],systemlist[1])
			unparalist[0] -= 1
			# if the amount has not matched the requirement, call the function for this mode again
			blocking (systemlist,paralist,unparalist,pinlist)
		
		# cs is gone after us
		else: 
			# turn on CS
			arduino.cs(pinlist[0],1)
			arduino.cs(paralist[1],1)
			# delay until US is supposed to present
			arduino.c_delay(paralist[0]+paralist[2],systemlist[1])
			# deliver food
			arduino.c_food("deliver",systemlist[0],pinlist[2],systemlist[1])
			# delay for the duration of US
			arduino.c_delay(paralist[1],systemlist[1])
			# remove food
			arduino.c_food("remove",systemlist[0],pinlist[2],systemlist[1])
			# delay until fulfill the duration of CS
			arduino.c_delay(paralist[0]+paralist[2]-paralist[1],systemlist[1])
			# turn off CS
			arduino.cs(pinlist[0],0)
			arduino.cs(pinlist[1],0)
			# delay for the paralist[3]-trial interval
			arduino.c_delay(paralist[3],systemlist[1])
			unparalist[0] -= 1
			# if the amount has not matched the requirement, call the function for this mode again
			forward (systemlist,paralist,unparalist,pinlist)

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])