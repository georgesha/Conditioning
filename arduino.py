import math
import time
import pyfirmata # Arduino Uno board
from time import sleep # achieve the delay

# record the time for each action
'''
starttime is the starttime of the program, 
output is the opened file, event is what is
going to be recorded:
'R' means the rat press the button with RR
'N' means the rat press the button with NR
'E' means enough times are pressed
'RL' means the rat release the button
'F' means start feeding
'S' means stop feeding
'SDE' means SD expired
'SDS' means a new SD start
'''
def recordtime(starttime, output, event): 
	if event == "R":
		outputstr = " : the rat press the button with RR"
	if event == "N":
		outputstr = " : the rat press the button with NR"
	if event == "E":
		outputstr = " : enough times are pressed"
	if event == "RL":
		outputstr = " : the rat release the button"
	if event == "F":
		outputstr = " : start feeding"
	if event == "S":
		outputstr = " : stop feeding"
	if event == "SDE":
		outputstr = " : SD expired"
	if event == "SDS":
		outputstr = " : a new SD start"
	processtime = time.time() - starttime
	hour = math.floor(processtime // 3600)
	minute = math.floor(processtime // 60 - (60 * hour))
	second = round(processtime % 60, 2)
	strtime = str(hour) + ":" + str(minute) + ":" + str(second)
	outputstr = strtime + outputstr
	output.write(outputstr + "\n")

# blink the LED to indicate the press leading to reward
def blink(top,LED):
	print("pressed")
	LED.write(1)
	top.update()
	sleep(0.1)
	LED.write(0)

# feed food
def food(f,board,servo,top):
    if f=="deliver":
        for i in range(0, 180):
            board.digital[servo].write(i) 
            # well-built function to control servo which make the user can directly write the angle of servo
            top.update()
            sleep(0.01)
    elif f=="remove":
        for i in range(180,0,-1):
            board.digital[servo].write(i) 
            # well-built function to control servo which make the user can directly write the angle of servo
            top.update()
            sleep(0.01) 

#delay
"""
sleep for certain seconds and record the useless presses
the reason that break down the delay is in order to update the condition to GUI window 
to avoid it fall into 'No responding'
also, during this process, useless presses can be detected and recorded
"""
def delay(time,starttime,buttonPin,output,board,top):
    """ 
    create a variable to achieve correct detection of the state of button
    it is initially set to zero, once the button is pressed, it changed to 1, indicating the button is pressed
    and it will be changed to zero again only when the button is released
    after it back to zero, another press will be detected and count as active press
    meanwhile, this variable can count for the rising and falling edge of button
    """
    ud=0
    i=0
    time=time*100
    while i<= time: # loop for delay
        i+=1
        top.update()
        sleep(0.01)
        if buttonPin.read() == 1:
            if ud == 0:
                ud = 1
                recordtime(starttime, output, "N")
            if ud == 1:
                if buttonPin.read() == 0:
                    recordtime(starttime, output, "RL")
                    ud = 0
                    
#the function controling action after the rat achieve the criterion
def achieve(duration,servoPin,buttonPin,starttime,output,board,top):
    # deliver the food and record the time down
    recordtime(starttime, output, "F")
    food("deliver",board,servoPin,top)
    # delay for the duration of reward
    delay(duration,starttime,buttonPin,output,board,top)
    # remove the food and record the time down
    recordtime(starttime, output, "S")
    food("remove",board,servoPin,top)
    return 0
    
#control CS according to state
def cs(green_state,red_state):
    greenPin.write(green_state)
    redPin.write(red_state)
   
#delay for classical
def c_delay(time,top):
    # consider for some cases that the delay is randomly selected
    if time=="random":
        time = float(random.randint(2,8))
        print ("interval: %s" % time)        
    i=1
    time = time * 100
    while i <=  time:
        i += 1
        top.update()
        sleep(0.01)   
