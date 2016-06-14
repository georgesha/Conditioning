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
import sys # correctly shut down the program


#define the sub-function for each mode

#forward
i1 = 1 # count for the number of trials
def forward (t,dur_c,dur_u,btw,inter,r,g):
    global i1 
    
    # if there is no overlap between CS and US
    if btw>=0:
        # write the state of LEDs according to the choice of user
        redPin.write(r)
        greenPin.write(g)
        
        # delay for duration of CS and turn off the LED
        # the reason that break down the delay is in order to update the condition to GUI window 
        # to avoid it fall into 'No responding'
        i=1
        dur_c_sec = dur_c * 100
        while i <=  dur_c_sec: # loop for delay
            i += 1
            top.update()
            sleep(0.01)
        redPin.write(0) # turn off LED
        greenPin.write(0)
        
        # delay for the interval between CS and US
        i=1
        btw_sec = btw * 100
        while i <=  btw_sec:
            i += 1
            top.update()
            sleep(0.01)
        
        # deliver the food using servo
        for i in range(0, 180):
            board.digital[servoPin].write(i) 
            # well-built function to control servo which make the user can directly write the angle of servo
            top.update()
            sleep(0.01)
        # delay for the duration of US
        dur_u_sec = dur_u * 100
        while i <=  dur_u_sec:
            i += 1
            top.update()
            sleep(0.01)
        # remove the food
        for i in range(180, 1, -1):
            board.digital[servoPin].write(i)
            top.update()
            sleep(0.01)
        
        # consider the choice of intertrial interval
        # if it is selected as random, the program will automatically selected from two to eight seconds
        if inter=="random":
            j = float(random.randint(2,8))
            print ("intertrial interval: %s" % j)
            # print the random choice out
            j_sec = j * 100
            while i <=  j_sec:
                i += 1
                top.update()
                sleep(0.01)
        else:
            sec = inter * 100
            while i <=  sec:
                i += 1
                top.update()
                sleep(0.01)
        
        # increase the number of trails
        i1 += 1
        # if the amount has not matched the requirement, call the function for this mode again
        if i1 <= t:
            forward (t,dur_c,dur_u,btw,inter,r,g)
            
    # if there is overlap between CS and US
    else:
        # If CS is gone before US
        if -1*btw<=dur_u: # -1 due to the negative value for overlap
            redPin.write(r)
            greenPin.write(g)
            
            # first delay for the time until US is supposed to present
            mix_sec = (dur_c+btw) * 100
            while i <=  mix_sec:
                i += 1
                top.update()
                sleep(0.01)
            
            # deliver the food
            for i in range(0, 180):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
            
            # keep presenting CS until the time of the overlap passes 
            # then turn off CS
            btw_sec = (-1*btw) * 100
            while i <=  btw_sec:
                i += 1
                top.update()
                sleep(0.01)
            redPin.write(0)
            greenPin.write(0)
            
            # keep presenting US until the time of it has been fulfilled
            # then remove the food
            mix_sec = (btw+dur_u) * 100
            while i <=  mix_sec:
                i += 1
                top.update()
                sleep(0.01)
            sleep(btw+dur_u)
            for i in range(180, 1, -1):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
                
            # intertrial interval
            if inter=="random":
                j = float(random.randint(2,8))
                print ("intertrial interval: %s" % j)
                j_sec = j * 100
                while i <=  j_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            else:
                sec = inter * 100
                while i <=  sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            
            # check if the number of trials matches
            i1 += 1
            if i1 <= t:
                forward (t,dur_c,dur_u,btw,inter,r,g)
        
        # cs is gone after us
        else: 
            redPin.write(r)
            greenPin.write(g)
            
            # first delay for the time until US is supposed to present
            # and deliver the food
            mix_sec = (dur_c+btw) * 100
            while i <=  mix_sec:
                i += 1
                top.update()
                sleep(0.01)
            for i in range(0, 180):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
                
            # delay for the time that US needs to be presented
            # then remove the food
            dur_u_sec = dur_u * 100
            while i <=  dur_u_sec:
                i += 1
                top.update()
                sleep(0.01)
            for i in range(180, 1, -1):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
                
            # keep presenting the CS until the time of it has been fulfilled
            # then turn off it
            mix_sec = (dur_c+btw-dur_u) * 100
            while i <=  mix_sec:
                i += 1
                top.update()
                sleep(0.01)
            sleep(dur_c+btw-dur_u)
            redPin.write(0)
            greenPin.write(0)
            
            # intertrial interval
            if inter=="random":
                j = float(random.randint(2,8))
                print ("intertrial interval: %s" % j)
                j_sec = j * 100
                while i <=  j_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            else:
                sec = inter * 100
                while i <=  sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            
            # check the number of trials
            i1 += 1
            if i1 <= t:
                forward (t,dur_c,dur_u,btw,inter,r,g)
                
#temporal
i2 = 1 # count for the number of trials
def temporal(t,dur_u,inter):
    global i2
    
    # deliver the food
    for i in range(0, 180):
        board.digital[servoPin].write(i)
        top.update()
        sleep(0.01)
    
    # stay for the duration of US
    dur_u_sec = dur_u * 100
    while i <=  dur_u_sec:
        i += 1
        top.update()
        sleep(0.01)
    
    # remove the food
    for i in range(180, 1, -1):
        board.digital[servoPin].write(i)
        top.update()
        sleep(0.01)
        
    # wait for the time of intertrial interval
    inter_sec = inter * 100
    while i <=  inter_sec:
        i += 1
        top.update()
        sleep(0.01)
        
    # increase the number of trials
    # if the amount has not matched the requirement, call the function for this mode again
    i2 += 1
    if i2 <= t:
        temporal(t,dur_u,inter)
        
#blocking
# this mode is similar to forward, except that it uses both red and green LEDs
i3 = 1
def blocking(t,dur_c,dur_u,btw,inter):
    global i3
    i = 1
    if btw>=0:
        while i <= t:
            redPin.write(1)
            greenPin.write(1)
            dur_c_sec = dur_c * 100
            while i <=  dur_c_sec:
                i += 1
                top.update()
                sleep(0.01)
            redPin.write(0)
            greenPin.write(0)
            btw_sec = btw * 100
            while i <=  btw_sec:
                i += 1
                top.update()
                sleep(0.01)
            for i in range(0, 180):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
            dur_u_sec = dur_u * 100
            while i <=  dur_u_sec:
                i += 1
                top.update()
                sleep(0.01)
            for i in range(180, 1, -1):
                board.digital[servoPin].write(i)
                top.update()
                sleep(0.01)
            if inter=="random":
                j = float(random.randint(2,8))
                print ("intertrial interval: %s" % j)
                j_sec = j * 100
                while i <=  j_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            else:
                inter_sec = inter * 100
                while i <=  inter_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
            i3 += 1
            if i3 <= t:
                blocking(t,dur_c,dur_u,btw,inter)
    else:
        if -1*btw<=dur_u: #cs is gone before us
            while i<=t:
                redPin.write(1)
                greenPin.write(1)
                mix_sec = (dur_c+btw) * 100
                while i <=  mix_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                for i in range(0, 180):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                btw_sec = (-1*btw) * 100
                while i <=  btw_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                redPin.write(0)
                greenPin.write(0)
                mix_sec = (btw+dur_u) * 100
                while i <=  mix_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                for i in range(180, 1, -1):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                if inter=="random":
                    j = float(random.randint(2,8))
                    print ("intertrial interval: %s" % j)
                    j_sec = j * 100
                    while i <=  j_sec:
                        i += 1
                        top.update()
                        sleep(0.01)
                else:
                    inter_sec = inter * 100
                    while i <=  inter_sec:
                        i += 1
                        top.update()
                        sleep(0.01)
                i3 += 1
                if i3 <= t:
                    blocking(t,dur_c,dur_u,btw,inter)
        else: #cs is gone after us
            while i<=t:
                redPin.write(1)
                greenPin.write(1)
                mix_sec = (dur_c+btw) * 100
                while i <=  mix_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                for i in range(0, 180):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                dur_u_sec = dur_u * 100
                while i <=  dur_u_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                for i in range(180, 1, -1):
                    board.digital[servoPin].write(i)
                    top.update()
                    sleep(0.01)
                mix_sec = (dur_c+btw-dur_u) * 100
                while i <=  mix_sec:
                    i += 1
                    top.update()
                    sleep(0.01)
                redPin.write(0)
                greenPin.write(0)
                if inter=="random":
                    j = float(random.randint(2,8))
                    print ("intertrial interval: %s" % j)
                    j_sec = j * 100
                    while i <=  j_sec:
                        i += 1
                        top.update()
                        sleep(0.01)
                else:
                    inter_sec = inter * 100
                    while i <=  inter_sec:
                        i += 1
                        top.update()
                        sleep(0.01)
                i3 += 1
                if i3 <= t:
                    blocking(t,dur_c,dur_u,btw,inter)



    
#function for start button
def onStartButtonPress():
    # disable the start button to avoid double-click during executing
    startButton.config(state=tkinter.DISABLED)
    
    # If user choose to pre-test
    # automatically start a trial that implement all the hardware
    # in order to check basic settings
    if preVar.get(): # if the box for pre-test is checked, it .get() will return '1'
        # assign simple paramters for pre-test
        t=1
        dur_c=5
        dur_u=3
        btw=-2
        inter='random'
        red=1
        green=1
        forward(t,dur_c,dur_u,btw,inter,red,green)
        
    # implement the experiment
    else:
        # whether load the configuration
        # if load, assign parameters from file and print them out
        if loadVar.get():
            with open('configuration_cc.csv', 'r', newline="") as f:
                r = csv.reader(f)
                data = None
                count = 0
                for row in r: # loop to read from the file
                    if count == 1:
                        data = row
                    count += 1
                t = float(data[0])
                dur_c = float(data[1])
                dur_u = float(data[2])
                btw = float(data[3])
                if data[4]=="random":
                    inter = data[4]
                else:
                    inter = float(data[4])
                red = data[5]
                green = data[6]
                mode = data[7]
                print("read result: ")
                print("trial times" + str(t))
                print("conditioned duration: " + str(dur_c))
                print("unconditioned duration: " + str(dur_u))
                print("interval between CS&US: " + str(btw))
                print("intertrial interval: " + str(inter))
        # if not load, get parameters from entries
        # and save them to the configuration files
        else:
            t = float(trial.get())
            dur_c = float(cs.get())
            dur_u = float(us.get())
            btw = float(between.get())
            if randomVar.get():
                inter = "random"
            else:
                inter = float(intertrial.get())
            if redVar.get():
                red = 1
            else:
                red = 0
            if greenVar.get():
                green = 1
            else:
                green = 0
            if forwardVar.get():
                mode = "f"
            elif temporalVar.get():
                mode = "t"
            elif blockingVar.get():
                mode = "b"
                red = 1
                green = 1
            with open('configuration_cc.csv', 'w', newline="") as f: # save parameters
                w = csv.writer(f)
                w.writerow(["number of trials", "CS duration", "US duration", "interval between CS and US", "intertrial interval","red LED","green LED","MODE"])
                data = [t, dur_c, dur_u, btw, inter,red,green,mode]
                w.writerow(data)   
                
        # check the choice for mode and call corresponding function
        if mode=="f":
            forward(t,dur_c,dur_u,btw,inter,red,green)
        elif mode=="t":
            temporal(t,dur_u,inter)
        elif mode=="b":
            blocking(t,dur_c,dur_u,btw,inter)

    startButton.config(state=tkinter.ACTIVE)
    
# define the function of exit
def pressexit():
    board.exit()
    top.destroy()
    sys.exit()




#associate the port
port = 'COM9'
board = pyfirmata.Arduino(port)

# Define pins and corresponding modes
greenPin = board.get_pin('d:11:o')
redPin = board.get_pin('d:12:o')
servoPin = 13
board.digital[servoPin].mode = pyfirmata.SERVO


# Initialize main windows with title and size
top = tkinter.Tk()
top.title("classical cdt")


# create the checkbox for pre-test mode
preVar = tkinter.IntVar()
preCheckBox = tkinter.Checkbutton(top,
                                  text="PRE-TEST MODE",
                                  variable=preVar)
preCheckBox.grid(column=2, row=1) # to manage the location on window


# create the checkbox for user to decide whether read previous configuration or not
loadVar = tkinter.IntVar()
loadCheckBox = tkinter.Checkbutton(top, text = "load config?", variable = loadVar)
loadCheckBox.grid(column = 2, row = 2)



#get parameters

#trails
tkinter.Label(top,
              text="trial: ").grid(column=1, row=3)
trial = tkinter.Entry(top)
trial.grid(column=2, row=3)
trial.focus_set()
tkinter.Label(top,
              text="times").grid(column=3, row=3)
   
#cs  
tkinter.Label(top,
              text="cs duration: ").grid(column=1, row=4)
cs = tkinter.Entry(top)
cs.grid(column=2, row=4)
cs.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=4)

#us   
tkinter.Label(top,
              text="us duration: ").grid(column=1, row=5)
us = tkinter.Entry(top)
us.grid(column=2, row=5)
us.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=5)  

#between cs&us
tkinter.Label(top,
              text="interval between cs&us: ").grid(column=1, row=6)
between = tkinter.Entry(top)
between.grid(column=2, row=6)
between.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=6)

tkinter.Label(top,
              text="(negative interval").grid(column=2, row=7)
tkinter.Label(top,
              text="means overlap) ").grid(column=3, row=7)

#intertrial
tkinter.Label(top,
              text="intertrial interval: ").grid(column=1, row=8)
intertrial = tkinter.Entry(top)
intertrial.grid(column=2, row=8)
intertrial.focus_set()
tkinter.Label(top,
              text="seconds").grid(column=3, row=8)
#whether intertrial interval is random
randomVar = tkinter.IntVar()
randomCheckBox = tkinter.Checkbutton(top,
                                  text="Random",
                                  variable=randomVar)
randomCheckBox.grid(column=4, row=8)    
          

          

#create the checkbox for conditioned stimulus
tkinter.Label(top,
              text="conditioned stimulus: ").grid(column=1, row=9)
              
#green
greenVar = tkinter.IntVar()
greenCheckBox = tkinter.Checkbutton(top,
                                  text="Green LED",
                                  variable=greenVar)
greenCheckBox.grid(column=2, row=9)

#red
redVar = tkinter.IntVar()
redCheckBox = tkinter.Checkbutton(top,
                                  text="Red LED",
                                  variable=redVar)
redCheckBox.grid(column=3, row=9)





# Create checkbox for different conditioning modes

tkinter.Label(top,
              text="conditioning mode: ").grid(column=1, row=10)
              
#forward conditioning
forwardVar = tkinter.IntVar()
forwardCheckBox = tkinter.Checkbutton(top,
                                  text="FORWARD",
                                  variable=forwardVar)
forwardCheckBox.grid(column=2, row=10)

#temporal conditioning
temporalVar = tkinter.IntVar()
temporalCheckBox = tkinter.Checkbutton(top,
                                  text="TEMPORAL",
                                  variable=temporalVar)
temporalCheckBox.grid(column=3, row=10)

#blocking
blockingVar = tkinter.IntVar()
blockingCheckBox = tkinter.Checkbutton(top,
                                  text="BLOCKING",
                                  variable=blockingVar)
blockingCheckBox.grid(column=4, row=10)






# Create Start and Exit button

startButton = tkinter.Button(top,
                             text="Start",
                             command=onStartButtonPress)
                             # call the function of start button
startButton.grid(column=2, row=11)
exitButton = tkinter.Button(top,
                            text="Exit",
                            command=pressexit)
                            # call the function of exit button
exitButton.grid(column=3, row=11)



# Start and open the window
top.mainloop()