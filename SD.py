"""
 SD conditioning

 Create a GUI window to make user enter parameters
 And implement the actions of presenting reward 
 according to whether the rat has achieved the criterion
 within the duration of presenting SD

 The circuit:
 * Red LED attached from pin 11 to +5V
 * Green LED attached from pin 12 to +5V
 * 560 Ohm resistors attached from pin 11&12 to GND
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
		output = "output_sd_" + str(now) + ".txt"

	open(output, 'w').close()
	title = open(str(output), 'a', newline='')
	title.write("Arduino " + str(num) + " SD" + "\n")
	title.close()

	# Using iterator thread to avoid buffer overflow
	it = pyfirmata.util.Iterator(board)
	it.start()

	# Define pins and corresponding mode
	operantPin = board.get_pin('d:3:i')
	csPin = board.get_pin('d:11:o')
	sdPin = board.get_pin('d:12:o')
	usPin = 13
	board.digital[usPin].mode = pyfirmata.SERVO

	# start time of the experiment
	starttime = time.time()

	# Initialize main windows with title
	top = tkinter.Tk()
	top.title("Arduino " + str(num) + " SD cdt")

	tkinter.Label(top, text = "Pretest: Y/N").grid(column = 1, row = 1)
	preEntry = tkinter.Entry(top)
	preEntry.grid(column=2, row=1) # to manage the location on window
	preEntry.focus_set()

	tkinter.Label(top, text = "Load: Y/N").grid(column = 1, row = 2)
	loadEntry = tkinter.Entry(top)
	loadEntry.grid(column = 2, row = 2)
	loadEntry.focus_set()

	# the times need to active the feeding
	tkinter.Label(top, text = "Criterion: ").grid(column = 1, row = 3)
	timesEntry = tkinter.Entry(top)
	timesEntry.grid(column = 2, row = 3)
	timesEntry.focus_set()

	# the interval between receive and act
	tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 4)
	intervalEntry = tkinter.Entry(top)
	intervalEntry.grid(column = 2, row = 4)
	intervalEntry.focus_set()

	# how long will the feeding last
	tkinter.Label(top, text = "Duration: ").grid(column = 1, row = 5)
	durationEntry = tkinter.Entry(top)
	durationEntry.grid(column = 2, row = 5)
	durationEntry.focus_set()

	# the interval between each time
	tkinter.Label(top, text = "SD Duration: ").grid(column = 1, row = 6)
	sdintervalEntry = tkinter.Entry(top)
	sdintervalEntry.grid(column = 2, row = 6)
	sdintervalEntry.focus_set()

	# the intertrial between each time
	tkinter.Label(top, text = "Intertrial interval: ").grid(column = 1, row = 7)
	intertrialEntry = tkinter.Entry(top)
	intertrialEntry.grid(column = 2, row = 7)
	intertrialEntry.focus_set()

	tkinter.Label(top, text = "trial times: ").grid(column = 1, row = 8)
	trialEntry = tkinter.Entry(top)
	trialEntry.grid(column = 2, row = 8)
	tkinter.Label(top, text = "times").grid(column = 3, row = 8)

	tkinter.Label(top, text = "length: ").grid(column = 1, row = 9)
	lengthEntry = tkinter.Entry(top)
	lengthEntry.grid(column = 2, row = 9)
	tkinter.Label(top, text = "hours").grid(column = 3, row = 9)

	systemlist = [board,top,starttime,output,num]
	entrylist = [preEntry,loadEntry,timesEntry,intervalEntry,durationEntry,sdintervalEntry,intertrialEntry,trialEntry,lengthEntry]
	pinlist = [operantPin,csPin,sdPin,usPin]


	# Create Start and Exit button

	# button for main function
	startButton = tkinter.Button(top, text="Start", command=lambda: pressbutton(systemlist,entrylist,pinlist,startButton))
	startButton.grid(column=1, row=10)

	# exit button
	exitButton = tkinter.Button(top, text="Exit", command=lambda: exit(board,top,csPin,sdPin))
	exitButton.grid(column=2, row=10)

	# Start and open the window
	top.mainloop()

def pressbutton(systemlist,entrylist,pinlist,startButton):
	upanddown = 0
	currenttimes = 0 # the times that the rat already press
	looptime = 0 # record the start time of each trail
	
	trialtimes = math.inf
	timelength = math.inf

	if entrylist[7].get() != "":
		trialtimes = int(entrylist[7].get())
	if entrylist[8].get() != "":
		timelength = float(entrylist[8].get()) * 3600 # change to second

	# disable the start button to avoid double-click during executing
	startButton.config(state=tkinter.DISABLED)
	
	# If user choose to pre-test
	# automatically start a trial that implement all the hardware
	# in order to check basic settings
	if entrylist[0].get() == "Y":
		inputlist = [pinlist[0]]
		outputlist = [pinlist[1],pinlist[2],pinlist[3]]
		arduino.pretest(systemlist[0], systemlist[1], inputlist, outputlist)

	# implement the experiment	
	else:
		# whether load the configuration
		# read from existing configuration
		if entrylist[1].get() == "Y":
			with open('configuration_sd.csv', 'r', newline='') as f:
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
				sdinterval = float(data[3])
				intertrial = float(data[4])
				print("times: " + str(times))
				print("interval: " + str(interval))
				print("duration: " + str(duration))
				print("sdinterval: " + str(sdinterval))
				print("intertrial: " + str(intertrial))
		# don't read from existing configuration and print them out
		else:
			# the value get from GUI window, need to be converted into floating number
			times = float(entrylist[2].get()) 
			interval = float(entrylist[3].get())
			duration = float(entrylist[4].get())
			sdinterval = float(entrylist[5].get())
			intertrial = float(entrylist[6].get())
			with open('configuration_sd.csv', 'w', newline='') as f:
				w = csv.writer(f)
				w.writerow(["times", "interval", "duration", "sdinterval", "intertrial"])
				data = [times, interval, duration, sdinterval, intertrial]
				w.writerow(data)
		looptime = time.time() # get the start time for the first trial
		pinlist[2].write(1) # turn on SD
		paralist = [times,interval,duration,sdinterval,intertrial]
		unparalist = [currenttimes,upanddown,looptime,trialtimes,timelength]
		para = open(str(systemlist[3]), 'a', newline='')
		para.write("times: " + str(times) + "\n")
		para.write("interval: " + str(interval) + "\n")
		para.write("duration: " + str(duration) + "\n")
		para.write("sdinterval: " + str(sdinterval) + "\n")
		para.write("intertrial: " + str(intertrial) + "\n")
		para.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		# begin the first trail
		# call the function that contains the main body
		run(systemlist,paralist,unparalist,pinlist)

def run(systemlist,paralist,unparalist,pinlist):
	if unparalist[3] == 0 or time.time() - systemlist[2] >= unparalist[4]:
		exit(systemlist[0], systemlist[1],pinlist[1],pinlist[2])
	# if the difference between current and the start point of the trial is the paralist[2] of sd
	# in this statement, use very closing value to represent the equal condition
	# because the loop will be called every 1ms, regarding the deviation, the range is better than exactly equal
	# this means that the rat has not achieved the criterion so that the sd is not turn off
	if (time.time() - unparalist[2]) > (paralist[3] - 0.001) and (time.time() - unparalist[2]) < (paralist[3] + 0.001):
		#calculate the relative time for the press
		arduino.recordtime(systemlist[2], systemlist[3], "SDE")
		pinlist[2].write(0) # turn off SD

		
		# wait for paralist[4] paralist[1]
		# the reason that break down the delay is in order to update the condition to GUI window 
		# to avoid it fall into 'No responding'
		# also, during this process, useless presses can be detected and recorded
		arduino.delay(paralist[4],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
					
		unparalist[0] = 0 # reset the value
		
		arduino.recordtime(systemlist[2], systemlist[3], "SDE")
		# if the count is greater than one, 
		# which means there remain some trails, start a new trial

		arduino.recordtime(systemlist[2], systemlist[3], "SDS")
		pinlist[2].write(1) # turn on SD
		unparalist[2] = time.time() # get the start time of the new trial
		
	unparalist[0],unparalist[1] = arduino.monitor(paralist[0], unparalist[0], unparalist[1], systemlist[2], systemlist[3], pinlist[0], pinlist[1], systemlist[1],systemlist[4])
			# if the rat achieve the criterion, that actions according to the time sequence
			# during this section, all actions and presses that do not lead to reward are recorded to file as well
	if unparalist[0] == paralist[0]:
		pinlist[2].write(0) # stop SD first
		arduino.recordtime(systemlist[2], systemlist[3], "E")
		arduino.delay(paralist[1],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
		unparalist[0] = arduino.us(paralist[2],pinlist[3],pinlist[0],systemlist[2],systemlist[3],systemlist[0],systemlist[1])
		# after feeding
		# wait for paralist[4] paralist[1] and record the useless presses
		arduino.delay(paralist[4],systemlist[2],pinlist[0],systemlist[3],systemlist[0],systemlist[1])
					
		# if the count is greater than one, 
		# which means there remain some trails, start a new trial
		arduino.recordtime(systemlist[2], systemlist[3], "SDS")
		pinlist[2].write(1)
		unparalist[3] -= 1
		print("times to go: " + str(unparalist[3]))
		print("time already pass: " + str(time.time() - systemlist[2]))		
		unparalist[2] = time.time() # get the start time of the new trial
	# recall itself every 1 milisecond in order to keep monitoring the press  
	systemlist[1].after(1,run,systemlist,paralist,unparalist,pinlist)

# exit button function
def exit(board,top,csPin,sdPin):
	csPin.write(0)
	sdPin.write(0)
	board.exit()
	top.destroy()



if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])