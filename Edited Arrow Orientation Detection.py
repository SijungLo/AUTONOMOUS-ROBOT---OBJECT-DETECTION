#### IMPORT MODULES
import cv2
from picamera2 import Picamera2
import numpy as np
import math
from libcamera import controls

def nothing(x):
    pass

#### SET TRACKBARS FOR CORNERS TO BE DETECTED 
cv2.namedWindow("rawCapture")
cv2.createTrackbar("quality","rawCapture",1,100,nothing)

#### RECORD THE CAPTURE

#### INITIALIZE THE CAPTURE
cv2.startWindowThread()
font = cv2.FONT_HERSHEY_SIMPLEX

# initialize the camera and grab a reference to the raw camera capture
camera = Picamera2()
WIDTH = 640
HEIGHT = 480
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (WIDTH, HEIGHT)}))
camera.start()
camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
while True:
    rawCapture = camera.capture_array()
#### FLIP THE VIDEO SINCE THE PI CAMERA IS INVERTED    
    rawCapture=cv2.flip(rawCapture,-1)
#### EDGE DETECTION    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(rawCapture, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_green = np.array([59,90,151])
    upper_green = np.array([83,255,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_green, upper_green)
    #Blurring the mask
    blur = cv2.GaussianBlur(mask,(9,9),0)

#### DETETCT THE CORNERS USING THE TRACKBARS
    quality = cv2.getTrackbarPos("quality","rawCapture")
    quality = quality/100
    corners = cv2.goodFeaturesToTrack(blur,5,quality,10)
    try:
        corners = np.intp(corners)
        #Plot the corners
        for i in corners:
            x,y = i.ravel()
            cv2.circle(rawCapture,(x,y),3,150,-1)

        
    #### GET THE CORNERS DATA FOR FINDING THE MIDPOINT OF THE ARROW
        for i in corners[0]:
            a0=i[0]
            b0=i[1]
        for i in corners[1]:
            a1=i[0]
            b1=i[1]
        for i in corners[2]:
            a2=i[0]
            b2=i[1]
        for i in corners[3]:
            a3=i[0]
            b3=i[1]
        for i in corners[4]:
            a4=i[0]
            b4=i[1]

    #### FIND THE MIDPOINT
        am=(a0+a1)/2
        bm=(b0+b1)/2
        #print(am,bm)

    #### FIND THE CONTOURS
        contours, hier = cv2.findContours(blur, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours=sorted(contours,key=lambda x:cv2.contourArea(x),reverse=True)

    #### DRAW A CIRCLE ARROUND THE ARROW TO FIND THE ANGLE OF THE ARROW
        for c in contours:
            # find minimum area
            x,y,w,h = cv2.boundingRect(c)
            (x,y),radius = cv2.minEnclosingCircle(c)
            center = (int(x),int(y))
            radius = int(radius)
            cv2.circle(rawCapture,center,radius,(0,255,0),2)
            cv2.circle(rawCapture,center,2,(0,255,0),2)
            cv2.circle(rawCapture,(int(am),int(bm)),2,(0,255,0),2)

        #Drawing lines
        cv2.line(rawCapture,center,(int(am),int(bm)),(255,0,0),1)
        cv2.line(rawCapture,center,(int(radius+x),int(y)),(255,0,0),1)

        #Angles
        atan=math.atan2(int(bm)-int(y),int(am)-int(x))
        angle=math.degrees(atan)
        print('angle=', angle)
        if(angle >= -45 and angle < 45):
            cv2.putText(rawCapture,'RIGHT',(10,85),font,1,(255,255,0))
            print("RIGHT")
        elif(angle >=45 and angle < 135):
            cv2.putText(rawCapture,'DOWN',(10,85),font,1,(255,255,0))
            print("DOWN")
        elif(angle >= -180 and angle <=-135): 
            cv2.putText(rawCapture,'LEFT',(10,85),font,1,(255,255,0))
            print("LEFT")
        elif(angle >=135 and angle <=180):
            cv2.putText(rawCapture,'LEFT',(10,85),font,1,(255,255,0))
            print("LEFT")
        elif(angle > -135 and angle < -45):
            cv2.putText(rawCapture,'UP',(10,85),font,1,(255,255,0))
            print("UP")
        cv2.imshow('rawCapture',rawCapture)
    #### SHOWING AND SAVING THE OUTPUT
    except:
        cv2.imshow('rawCapture', rawCapture)
        continue
