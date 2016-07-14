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
import math # help do calculation when getting ralative time
from random import randint # to randomly select from a range or a list
import arduino

# inital variables
times = 0 # how many times does the rat need to get the reward
interval = 0 # the interval between receiving input from button and begin feeding
duration = 0 # how long staying feeding
step = 0
gap = 0

# associate the port
port = 'COM7'
board = pyfirmata.Arduino(port)

# Using iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define pins
buttonPin = board.get_pin('d:3:i')
servoPin = 13
board.digital[servoPin].mode = pyfirmata.SERVO
LEDPin = board.get_pin('d:11:o')

# start time of the experiment
starttime = time.time()

# open the file and save actions during experiment
output = open('output_p.txt', 'w', newline='')


currenttimes = 0 # create a variable to count the presses that lead to reward
totaltimes = 0 # create a variable to count the total trials the rat has completed used to decide the increment

# create a variable to achieve correct detection of the state of button
# it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
# and it will be changed to zero again only when the button is released
# after it back to zero, another press will be detected and count as active press
# meanwhile, this variable can count for the rising and falling edge of button
upanddown = 0


# main function
def pressbutton():
    global times
    global interval
    global duration
    global step
    global gap

    # disable the start button to avoid double-click during executing
    startButton.config(state=tkinter.DISABLED)

    # If user choose to pre-test
    # automatically start a trial that implement all the hardware
    # in order to check basic settings
    if preVar.get():
        # let the user to press once to check button's function
        print ('please press the button once')
        currenttimes = 0
        upanddown = 0
        while True:
            if buttonPin.read() == 1: # if button is pressed, .read() will return 1
                if upanddown == 0:
                    upanddown = 1
                    LEDPin.write(1)
                    top.update()
                    sleep(0.1)
                    LEDPin.write(0) # make the LED blink once to indicate the press lead to reward
                    currenttimes += 1;
                    
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
                        currenttimes = 0 # reset currenttimes
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
            if randomVar.get():
                step="random"
            else:
                step=int(stepEntry.get())
            gap = int(gapEntry.get())
            with open('configuration_p.csv', 'w', newline="") as f: # save parameters
                w = csv.writer(f)
                w.writerow(["Number of press", "Interval between press and feed", "Duration of feeding","Incresing step","Trials between increment"])
                data = [times, interval, duration,step,gap]
                w.writerow(data)
                
        # read from existing configuration and print them out
        else:
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
    
    # call the function that contains the main body
    run()
    
interval=interval*100
duration=duration*100 # used for delay

def run():    
    global currenttimes
    global upanddown
    global totaltimes
    global times
    global interval
    global duration
    global step
    global gap
    currenttimes,upanddown = arduino.monitor(times, currenttimes, upanddown, starttime, output, buttonPin, LEDPin, top)
    # if the rat achieve the criterion, that actions according to the time sequence
    # during this section, all actions and presses that do not lead to reward are recorded to file as well
    if currenttimes == times:
        arduino.recordtime(starttime, output, "E")
        arduino.delay(interval,starttime,buttonPin,output,board,top)
        #record the time that it achieves the criterion                
        currenttimes = arduino.us(duration,servoPin,buttonPin,starttime,output,board,top)
        
        # for every certain trails, the criterion need to be increased
        # the trails that increase the criterion is the number that dividable by 'gap'
        if totaltimes % gap==0:
            if step=="random":
                s=randint(1,3) # if user select random as step, randomly select it from one to three
                print (s) # and print this step out
                times+=s
            else:
                times+=step
        print("current times is: " + str(times)) # print the current criterion out
    
    # recall itself every 1milisecond in order to keep monitoring the press     
    top.after(1,run)


# exit button function
def exit():
    LEDPin.write(0)
    board.exit()
    top.destroy()
    sys.exit()




# Initialize main windows with title and size
top = tkinter.Tk()
top.title("P Ratio")

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
tkinter.Label(top, text = "starting criterion: ").grid(column = 1, row = 3)
timesEntry = tkinter.Entry(top)
timesEntry.grid(column = 2, row = 3)
timesEntry.focus_set()
tkinter.Label(top,
              text="presses").grid(column=3, row=3)


# the interval between completing of pressing and feeding food
tkinter.Label(top, text = "Interval: ").grid(column = 1, row = 4)
intervalEntry = tkinter.Entry(top)
intervalEntry.grid(column = 2, row = 4)
intervalEntry.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=4)


# how long will the feeding last
tkinter.Label(top, text = "Duration of food: ").grid(column = 1, row = 5)
durationEntry = tkinter.Entry(top)
durationEntry.grid(column = 2, row = 5)
durationEntry.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=5)

# how many presses to increase as progressive ratio
tkinter.Label(top,
              text="increasing step:").grid(column=1, row=6)
stepEntry = tkinter.Entry(top)
stepEntry.grid(column=2, row=6)
tkinter.Label(top,
              text="presses").grid(column=3, row=6)
randomVar=tkinter.IntVar()
randomBox = tkinter.Checkbutton(top,
                                  text="random",
                                  variable=randomVar)
randomBox.grid(column=4, row=6)
 
# every how many trials does the criterion increase  
tkinter.Label(top,
              text="trial interval of each increment:").grid(column=1, row=7)
gapEntry = tkinter.Entry(top)
gapEntry.grid(column=2, row=7)
tkinter.Label(top,
              text="times").grid(column=3, row=7)
    


# Create Start and Exit button

# button for main function
startButton = tkinter.Button(top, text="Start", command=pressbutton)
startButton.grid(column=2, row=8)

# exit button
exitButton = tkinter.Button(top, text="Exit", command=exit)
exitButton.grid(column=3, row=8)

top.mainloop()