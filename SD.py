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
import math # help do calculation when getting ralative time
import arduino

# inital variables
trials = 0
times = 0 
interval = 0 
duration = 0
sdinterval = 0
intertrial = 0

#associate the port
port = 'COM7'
board = pyfirmata.Arduino(port)

# Using iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define pins and corresponding mode
buttonPin = board.get_pin('d:3:i')
LEDPin = board.get_pin('d:11:o')
sdPin = board.get_pin('d:12:o')
servoPin = 13
board.digital[servoPin].mode = pyfirmata.SERVO


# create a variable to achieve correct detection of the state of button
# it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
# and it will be changed to zero again only when the button is released
# after it back to zero, another press will be detected and count as active press
# meanwhile, this variable can count for the rising and falling edge of button
upanddown = 0
currenttimes = 0 # the times that the rat already press
looptime = 0 # record the start time of each trail

# open the file and save actions during experiment
output = open('output_sd.txt', 'w', newline='')

# start time of the experiment
starttime = time.time()

def startpressbutton():
    global trials
    global times
    global interval
    global duration
    global sdinterval
    global intertrial
    global looptime
    global upanddown
    global currenttimes
    
    # disable the start button to avoid double-click during executing
    startButton.config(state=tkinter.DISABLED)
    
    # If user choose to pre-test
    # automatically start a trial that implement all the hardware
    # in order to check basic settings
    if preVar.get():
        sdPin.write(1)
        print ('please press the button once')
        if buttonPin.read() == 1: # if button is pressed, .read() will return 1
            if upanddown==0:
                sdPin.write(0)
                LEDPin.write(1)
                sleep(0.1)
                LEDPin.write(0) # make the LED blink once to indicate the press lead to reward
                currenttimes += 1 # count it into presses that lead to reward
                
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
            # the value get from GUI window, need to be converted into floating number
            trials = float(trialsEntry.get())
            times = float(timesEntry.get()) 
            interval = float(intervalEntry.get())
            duration = float(durationEntry.get())
            sdinterval = float(sdintervalEntry.get())
            intertrial = float(intertrialEntry.get())
            with open('configuration_sd.csv', 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["trials", "times", "interval", "duration", "sdinterval", "intertrial"])
                data = [trials, times, interval, duration, sdinterval, intertrial]
                w.writerow(data)
        # read from existing configuration and print them out
        else:
            with open('configuration_sd.csv', 'r', newline='') as f:
                r = csv.reader(f)
                data = None
                count = 0
                for row in r:
                    if count == 1:
                        data = row
                    count += 1
                trials = float(data[0])
                times = float(data[1])
                interval = float(data[2])
                duration= float(data[3])
                sdinterval = float(data[4])
                intertrial = float(data[5])
                print("trials: " + str(trials))
                print("times: " + str(times))
                print("interval: " + str(interval))
                print("duration: " + str(duration))
                print("sdinterval: " + str(sdinterval))
                print("intertrial: " + str(intertrial))
                
        looptime = time.time() # get the start time for the first trial
        sdPin.write(1) # turn on SD
        # begin the first trail
        # call the function that contains the main body
        run()

def run():
    global trials
    global times
    global interval
    global duration
    global sdinterval
    global intertrial
    global upanddown
    global currenttimes
    global looptime
    

    # if the difference between current and the start point of the trial is the duration of sd
    # in this statement, use very closing value to represent the equal condition
    # because the loop will be called every 1ms, regarding the deviation, the range is better than exactly equal
    # this means that the rat has not achieved the criterion so that the sd is not turn off
    if (time.time() - looptime) > (sdinterval - 0.001) and (time.time() - looptime) < (sdinterval + 0.001):
        #calculate the relative time for the press
        arduino.recordtime(starttime, output, "SDE")
        sdPin.write(0) # turn off SD

        
        # wait for intertrial interval
        # the reason that break down the delay is in order to update the condition to GUI window 
        # to avoid it fall into 'No responding'
        # also, during this process, useless presses can be detected and recorded
        arduino.delay(intertrial,starttime,buttonPin,output,board,top)
                    
        currenttimes = 0 # reset the value
        
        arduino.recordtime(starttime, output, "SDE")
        
        trials -= 1 # finish a trial and decrease the count by 1

        # if the count is greater than one, 
        # which means there remain some trails, start a new trial
        if trials == 0:
            exit()
        arduino.recordtime(starttime, output, "SDS")
        sdPin.write(1) # turn on SD
        looptime = time.time() # get the start time of the new trial
        
    if buttonPin.read() == 1:
        if upanddown == 0:
            print("pressed")
            upanddown = 1
            arduino.recordtime(starttime, output, "R")
            LEDPin.write(1)
            top.update()
            sleep(0.1)
            LEDPin.write(0)
            currenttimes += 1 # increase the number of presses that lead to reward
            
            # if the rat achieve the criterion, that actions according to the time sequence
            # during this section, all actions and presses that do not lead to reward are recorded to file as well
            if currenttimes == times:
                sdPin.write(0) # stop SD first
                arduino.recordtime(starttime, output, "E")
                arduino.delay(interval,starttime,buttonPin,output,board,top)
                currenttimes = arduino.achieve(duration,servoPin,buttonPin,starttime,output,board,top)
                trials -= 1 # finish a trial and decrease the trial by 1
                # after feeding
                # wait for intertrial interval and record the useless presses
                arduino.delay(intertrial,starttime,buttonPin,output,board,top)
                            
                # if the count is greater than one, 
                # which means there remain some trails, start a new trial
                if trials == 0:
                    exit()
                arduino.recordtime(starttime, output, "SDS")
                sdPin.write(1)
                looptime = time.time() # get the start time of the new trial
    if upanddown == 1:
        if buttonPin.read() == 0:
            # record the releasing of the button
            arduino.recordtime(starttime, output, "RL")
            upanddown = 0
    # recall itself every 1 milisecond in order to keep monitoring the press  
    top.after(1,run)


# exit button function
def exit():
    sdPin.write(0)
    LEDPin.write(0)
    board.exit()
    top.destroy()
    sys.exit()


# Initialize main windows with title
top = tkinter.Tk()
top.title("SD cdt")

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

# the number of trials
tkinter.Label(top, text = "trials: ").grid(column = 1, row = 3)
trialsEntry = tkinter.Entry(top)
trialsEntry.grid(column = 2, row = 3)
trialsEntry.focus_set()

# the times need to active the feeding
tkinter.Label(top, text = "Criterion: ").grid(column = 1, row = 4)
timesEntry = tkinter.Entry(top)
timesEntry.grid(column = 2, row = 4)
timesEntry.focus_set()

# the interval between receive and act
tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 5)
intervalEntry = tkinter.Entry(top)
intervalEntry.grid(column = 2, row = 5)
intervalEntry.focus_set()

# how long will the feeding last
tkinter.Label(top, text = "Duration: ").grid(column = 1, row = 6)
durationEntry = tkinter.Entry(top)
durationEntry.grid(column = 2, row = 6)
durationEntry.focus_set()

# the interval between each time
tkinter.Label(top, text = "SD Duration: ").grid(column = 1, row = 7)
sdintervalEntry = tkinter.Entry(top)
sdintervalEntry.grid(column = 2, row = 7)
sdintervalEntry.focus_set()

# the intertrial between each time
tkinter.Label(top, text = "Intertrial interval: ").grid(column = 1, row = 8)
intertrialEntry = tkinter.Entry(top)
intertrialEntry.grid(column = 2, row = 8)
intertrialEntry.focus_set()


# Create Start and Exit button

# button for main function
startButton = tkinter.Button(top, text="Start", command=startpressbutton)
startButton.grid(column=2, row=9)

# exit button
exitButton = tkinter.Button(top, text="Exit", command=exit)
exitButton.grid(column=3, row=9)



# Start and open the window
top.mainloop()