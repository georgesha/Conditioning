"""
 Locate the rat and give reward accordingly


 use the knowledege of computer vision,
 to develop a program to make PC realize the location of rat
 through a real-time surveillance video
 
 and based on this kind of recognization, 
 reward can be automatically delivered to the rat
 if the rat gives certain movement that experimenter expectes
 i.e, if the rat move to certain corner of the experiment box

 """


# Import all needed libraries
import csv # saving information to files
import cv2 # load the vedio and do a series of process on it
import time # give the rative time to record actions 
import math # help do necessary calculation
import numpy as np
from scipy.cluster.vq import vq, kmeans, kmeans2, whiten

#_______________________________________________________________________________________#
#_______________________________________________________________________________________#


# inital variables
fps = 0 # count the frame
startframe = 0 # record the background of experiment environment
currentframe = 0 # record the current frame from vedio


# longest column and row for previous frame
precolumn = 0
prerow = 0
count = 0 # a threshold that determine whether it is an unstable noise

# get the start time of experiment for calculating relative time in the experiment
starttime=time.time()


#_______________________________________________________________________________________#
#_______________________________________________________________________________________#


# caputure the vedio from camera
cap = cv2.VideoCapture('SDV_0003.MP4')

# open the file and save records during experiment
f = open('rat_position.csv', 'w', newline='')
w = csv.writer(f)
w.writerow(["Time", "[x,y]"]) # the file is saved in terms of relative time and the coordinate of position 


#_______________________________________________________________________________________#
#_______________________________________________________________________________________#

#let the user enter the rewarding range

x1 = int(input("Please enter x: ")) 
y1 = int(input("Please enter y: ")) # get the left-upper corner of rewarding range
l = int(input("Please enter the length of the square area of rewarding: "))
x2 = x1 + l
y2 = y1 + l

# initial variable used to determine the situation to deliver reward
# because only if the rat stay in the range for some time,
# the reward will be de delivered
countreward = 0 

frame_interval = 200 # define the number of frames that will be ignore after a reward
intervalcount = 0 # count interval for frame_interval

# create a variable to indicate whether the rat is in the rewarding range
state =0

# create a variable to tell that the reward is delivered
reward = None

#_______________________________________________________________________________________#
#_______________________________________________________________________________________#


# main body to proces the frame from vedio

while(True):
	print(fps)
	# Capture frame-by-frame
	vget,frame = cap.read()
	
	# if nothing can be captured, then break the loop
	if vget == False:
		break


	# if it is the first frame of vedio, then save as the background
	if fps == 0:
		startframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert it into grayscale
		# blur the image by Gaussian blurring to reduce the effect of noise
		# (the degree of blurring can be adjusted accordingly)
		startframe = cv2.GaussianBlur(startframe, (5, 5), 0) 
  
	# if it's not the fist frame, save as current frame for latering comparison
	else:
		currentframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		currentframe = cv2.GaussianBlur(currentframe, (5, 5), 0)


	# if the program is quit by user, jump out of the loop
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


	# get the different of each pixel between current frame and background
	diff = cv2.absdiff(startframe, currentframe)
	# set a threshold (90) to determine whether the difference is siginificant enough
	# if difference is bigger, 'thresh' will be set to the max_value, which is 255	
	# otherwise, set to zero
	# and save the second column which contains the 2-dimensional resulted list to 'thresh'
	thresh = cv2.threshold(diff, 90, 255, cv2.THRESH_BINARY)[1]
	cv2.imshow("test", thresh)

#_______________________________________________________________________________________#

	"""
	Algorithm to determine the location of rat is:
	determine the largest length cantaining difference from background 
	in both vertical and horizontal directions in each frame
	and consider the cross of that column and rwo is the center of the rat
	"""

	# get the longest column and row
	position = np.array(list(zip(*np.where(thresh == 255))))
	position = position.astype(float)

	column = 0
	row = 0

	if len(position) != 0:
		cresult1 = kmeans2(position, 1, minit='points')
		column = math.floor(cresult1[0][0][0])
		row = math.floor(cresult1[0][0][1])
		cresult2 = kmeans2(position, 2, minit='points')
		column1 = math.floor(cresult2[0][0][0])
		row1 = math.floor(cresult2[0][0][1])
		column2 = math.floor(cresult2[0][1][0])
		row2 = math.floor(cresult2[0][1][1])
	'''
	if math.sqrt((precolumn - column1) ** 2 + (prerow - row1) ** 2) < math.sqrt((precolumn - column) ** 2 + (prerow - row) ** 2):
		column = column1
		row = row1
	elif math.sqrt((precolumn - column2) ** 2 + (prerow - row2) ** 2) < math.sqrt((precolumn - column) ** 2 + (prerow - row) ** 2):
		column = column2
		row = row2
	'''
	if math.sqrt((column1 - column2) ** 2 + (row1 - row2) ** 2) > 100:
		if math.sqrt((precolumn - column1) ** 2 + (prerow - row1) ** 2) < math.sqrt((precolumn - column2) ** 2 + (prerow - row2) ** 2):
			column = column1
			row = row1
		else:
			column = column2
			row = row2

	precolumn = column
	prerow = row

	# draw a rectangle to indicate the location of the rat
	for i in range(10):
		for j in range(10):
			frame[column + i - 5][row + j - 5] = ([255, 0, 0]) # set the color to blue
			#frame[column1 + i - 5][row1 + j - 5] = ([0, 255, 0])
			#frame[column2 + i - 5][row2 + j - 5] = ([0, 255, 0])

#_______________________________________________________________________________________#

	# check the situation for reward

	# display the rewarding range which is a square
	for i in range(l):
		for j in range(l):
			if i == 0 or i == l-1 or j == 0 or j == l-1:
				frame[x1 + i][y1 + j] = ([0, 255, 0]) # make it in color of green

	# check wether the rat locates in the range
	# if yes, increase the variable that counts for it by one
	# but, the rat must stay continuously in the range,
	# once it runs out of the range, count will be reset
	if row > x1 and row < x2 and column > y1 and column < y2:
		countreward += 1
		state=1
	else:
		countreward = 0
		state=0

	# check if the situation is when the reward is delivered just now
	# so no more reward should be delivered even the rat is relized in the rewarding range 
	if intervalcount == 0:
		# only if the rat has stayed in the range for enough frame
		# not reaching rewarding range (count==0) and not enough time in this range (count<30)
		# will not lead to reward
		if countreward == 30:
			processtime = time.time() - starttime
			hour = math.floor(processtime // 3600)
			minute = math.floor(processtime // 60 - (60 * hour))
			second = round(processtime % 60, 2)
			strtime = str(hour) + ":" + str(minute) + ":" + str(second)
			outputstr = strtime + " deliver food"
			print(outputstr) # this statement should be modified to deliver the food
			countreward = 0 # reset count
			intervalcount = frame_interval
			reward = "reward!"
	# if the reward has been delivered just now
	# instead of delivering, decrease the interval count by one until it equals zero again
	else:
		intervalcount -= 1 
		countreward = 0


#_______________________________________________________________________________________#

	# calculate the relative time for each frame
	processtime = time.time() - starttime # unit in second
	hour = math.floor(processtime // 3600) # calculate hour
	minute = math.floor(processtime // 60 - (60 * hour)) # calculate minute
	second = round(processtime % 60, 2) # calculate seconds containing 2 digit of siginificant figures
	currenttime = str(hour) + ":" + str(minute) + ":" + str(second) # time in the form of hh:mm:ss.xx

	# get the coordinate and write information to the file
	position = "[" + str(row) + ", " + str(column) + "]"

	# record the time, position and if it leads to reward down 
	data = [currenttime, position,state,reward]
	w.writerow(data)


	# display the result on screen
	#print(fps)
	cv2.imshow("result", frame) # play the vedio after processed frame by frame

 
#_______________________________________________________________________________________#

	# set variables for next frame
	fps += 1 # increase the count of frame
 
	# save current information as previous one for calculation of next frame
	precolumn = column
	prerow = row


#_______________________________________________________________________________________#
#_______________________________________________________________________________________#

 
# terminate the program
cap.release()
cv2.destroyAllWindows()