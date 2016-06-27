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
import math # help do calculation when getting ralative time
import arduino

# inital variables
times = 0 # how many times does the rat need to get the reward
interval = 0 # the interval between receiving input from button and begin feeding
duration = 0 # how long staying feeding

# associate the port
port = 'COM7'
board = pyfirmata.Arduino(port)

# Using iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define pins and select corresponding modes
buttonPin = board.get_pin('d:3:i')
servoPin = 13
board.digital[servoPin].mode = pyfirmata.SERVO
LEDPin = board.get_pin('d:11:o')

# start time of the experiment
starttime = time.time()

# open the file and save actions during experiment
output = open('output_fix.txt', 'w', newline='')


currenttimes = 0 # the times that the rat already press
upanddown = 0 # save the status of button


# main function when start button is pressed
def pressbutton():
    global times
    global interval
    global duration
    # disable the start button to avoid double-click during executing
    startButton.config(state=tkinter.DISABLED)
    
    # If user choose to pre-test
    # automatically start a trial that implement all the hardware
    # in order to check basic settings
    if preVar.get():
        # let the user to press once to check button's function
        print ('please press the button once')
        
        # create a variable to count the presses that lead to reward
        currenttimes = 0
        
        # create a variable to achieve correct detection of the state of button
        # it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
        # and it will be changed to zero again only when the button is released
        # after it back to zero, another press will be detected and count as active press
        # meanwhile, this variable can count for the rising and falling edge of button
        upanddown = 0
        
        while True:
            if buttonPin.read() == 1: # if button is pressed, .read() will return 1
                if upanddown == 0:
                    upanddown = 1
                    LEDPin.write(1)
                    top.update()
                    sleep(0.1)
                    LEDPin.write(0) # make the LED blink once to indicate the press lead to reward
                    currenttimes += 1
                    
                    # if one press is detected, deliver the food
                    if currenttimes == 1:
                        print ('press completed')
                        top.update()            
                        sleep(1)
                        print ('start feeding')
                        arduino.food("deliver",board,servoPin,top)
                        print ('stay feeding')
                        sleep(2)
                        print ('feeding end')
                        arduino.food("remove",board,servoPin,top)
                        currenttimes = 0 # reset for a new trail                 
                if upanddown == 1:
                    if buttonPin.read() == 0:
                        upanddown = 0    
    # implement the experiment                   
    else:
        # whether load the configuration
        # don't read from existing configuration
        if loadVar.get() == 0:
            times = float(timesEntry.get()) # the value get from GUI window, need to be converted into floating number
            interval = float(intervalEntry.get())
            duration = float(durationEntry.get())
            with open('configuration_fix.csv', 'w', newline='') as f: # save parameters
                w = csv.writer(f)
                w.writerow(["Number of times", "Interval between two times", "Duration of feeding"])
                data = [times, interval, duration]
                w.writerow(data)
                
        # read from existing configuration and print them out
        else:
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
                print("times: " + str(times))
                print("interval: " + str(interval))
                print("duration: " + str(duration))
    
    # call the function that contains the main body
    run()

def run():
    global interval
    global duration
    global times
    global currenttimes
    global upanddown
    if buttonPin.read() == 1:
        if upanddown == 0:
            upanddown = 1
            arduino.recordtime(starttime, output, "R")
            arduino.blink(top, LEDPin)
            currenttimes += 1; # increase the number of presses that lead to reward
            
            # if the rat achieve the criterion, that actions according to the time sequence
            # during this section, all actions and presses that do not lead to reward are recorded to file as well
            if currenttimes == times:
                arduino.recordtime(starttime, output, "E")
                arduino.delay(interval,starttime,buttonPin,output,board,top)
                currenttimes = arduino.achieve(duration,servoPin,buttonPin,starttime,output,board,top)
    if upanddown == 1:
        if buttonPin.read() == 0:
            # record the releasing of the button
            arduino.recordtime(starttime, output, "RL")
            upanddown = 0
            
    # recall itself every 1milisecond in order to keep monitoring the press       
    top.after(1,run)

# exit button function
def exit():
    board.exit()
    top.destroy()
    sys.exit()


# Initialize main windows with title and size
top = tkinter.Tk()
top.title("Fix Ratio")

#create the checkbox for pre-test
preVar = tkinter.IntVar()
preCheckBox = tkinter.Checkbutton(top,
                                  text="PRE-TEST MODE",
                                  variable=preVar)
preCheckBox.grid(column=2, row=1) # to manage the location on window

# create the checkbox for user to decide whether read previous configuration or not
loadVar = tkinter.IntVar()
loadCheckBox = tkinter.Checkbutton(top, text = "load config?", variable = loadVar)
loadCheckBox.grid(column = 2, row = 2)



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


# Create Start and Exit button

# button for main function
startButton = tkinter.Button(top, text="Start", command=pressbutton)
startButton.grid(column=1, row=6)

# exit button
exitButton = tkinter.Button(top, text="Exit", command=exit)
exitButton.grid(column=1, row=7)


# Start and open the window
top.mainloop()