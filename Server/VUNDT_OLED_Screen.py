# @author Matthew Burruss
# @date 12/21/2018
# @description A python script to control a 128x64 OLED Screen
from DepthSensor import Sensor
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import serial
import math
import subprocess
from VUNDT_OLED_Classes import Compass,DepthAndTempGuage,OxygenGauge,KickCounter,DiveTime,HomeScreen,Alert,SafetyFeatures
from KickCountingAlgorithm import FSM
# imports for IMU
import sys
import os
sys.path.append('/home/pi/Desktop/SeniorDesign/SeniorDesign')
from Adafruit_BNO055 import BNO055
import shutil
from threading import Thread
import threading
import csv
import datetime
from datetime import datetime
import numpy as np
#import cv2

import serial
#ser = serial.Serial('/dev/ttyACM0', 9600)

class HUD:
    def __init__(self):
        self.RST = None
        self.DC = 23
        self.SPI_PORT = 0
        self.SPI_DEVICE = 0
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=self.RST)
        self.disp.begin()
        # Clear display.
        self.disp.clear()
        self.disp.display()
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        # Load default font.
        self.font = ImageFont.load_default()
        # make screen blank
        self.blankScreen()
        # init components
        self.compass = Compass()
        self.depthAndTempMonitor = DepthAndTempGuage("metric")
        #self.oxygenMonitor = OxygenGauge()
        self.kickMonitor = KickCounter()
        self.timeMonitor = DiveTime()
        self.timeMonitor.startTimer()
        self.homeScreen = HomeScreen()
        self.safetyFeatures = SafetyFeatures()
        self.alert = Alert()
        self.shouldDisplayAlert = False
        self.alertMessage = ""
        self.alertTime = 0
        self.heading = 0
        self.depth = 0
        self.safetyStopBoolean = False # set to True when we have gone below diveHusBegunLimit
        self.diveHasBegunLimitMeters = 5 # depth at which if you go up, safety stop will begin
        self.safetyStopBeginDepth = 6 # meters at which upon rising, safety stop begins
        self.lastTimeScreenUpdated = time.time()
        self.calibrationAdjustment = 80
        self.lowestDepth = 0
        self.depthSum = 0
        self.tempSum = 0
        self.depthReadings = 0
        self.diveComplete = False
        self.totalDiveTime = 0
        self.kicks = 0
        self.totalKicks = 0
        self.arduinoCounter = 0
        self.markerSet = False
        self.displayLogo()
        #for i in range(10):
        #    print("Drawing loading Screen")
        #    self.displayLoadingScreen()
        # for demonstration
    # resets all booleans
    def reset(self):
        self.shouldDisplayAlert = False
        self.safetyStopBoolean = False # set to True when we have gone below diveHusBegunLimit
        self.initiateSafetyStop = False # When diver begins to surface, this will be set true.
        self.diveComplete = False
        self.kicks = 0

    def calibrateIMU(self,bno):
        sys = 0
        while sys != 3:
            sys, gyro, accel, mag = bno.get_calibration_status()
            print(sys)
            self.displayLoadingScreen()
    # resets the screen
    # should be cal)led to refresh the screen between writes
    def blankScreen(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
    
    def loadScreen(self):
        # Display image.
        # self.image.transpose(Image.FLIP_LEFT_RIGHT)
        if (self.shouldDisplayAlert):
            if (self.alertTime > time.time()):
                self.alert.sendAlert(self.alertMessage,45,self.draw)
            else:
                self.shouldDisplayAlert = False
        self.disp.image(self.image.transpose(Image.FLIP_LEFT_RIGHT))
        self.disp.display()

    def showImage(self,image):
        self.blankScreen()
        self.disp.image(self.image)
        self.disp.display()

    def displayLogo(self):
        self.blankScreen()
        self.image = self.homeScreen.drawLogo()
        self.loadScreen()
        time.sleep(3)
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def displayLoadingScreen(self):
        self.blankScreen()
        self.homeScreen.drawLoadScreen(self.draw)
        self.loadScreen()
        time.sleep(0.5)
    
    def NotifyDiverOfAscentSpeed(self):
        self.blankScreen()
        self.safetyFeatures.AscendingorDescendingTooQuickly(self.draw)
        tmp = self.shouldDisplayAlert
        self.shouldDisplayAlert = False
        self.loadScreen()
        self.shouldDisplayAlert = tmp
        time.sleep(0.3)
        self.blankScreen()

    def displayPreviousDives(self,index):
        self.blankScreen()
        index = self.safetyFeatures.displayPreviousDiveData(self.draw,index)
        self.loadScreen()
        time.sleep(0.3)
        return index
    def isDiveComplete(self):
        return self.diveComplete

    def incrementKicks(self,i):
        if (i == self.arduinoCounter + 1):
            self.kicks = self.kicks + 1
            self.totalKicks = self.totalKicks + 1
        self.arduinoCounter = i
    def saveDive(self):
        avgDepthData = str(round(float(self.depthSum)/float(self.depthReadings),1))
        lowDepthData = str(round(self.lowestDepth,1))
        tempData = str(round(float(self.tempSum)/float(self.depthReadings),1))
        elapsedTime = self.timeMonitor.getTime()
        diveTimeData = str(int(elapsedTime/60)) + ":" + str(int(elapsedTime%60))
        self.totalDiveTime = diveTimeData
        totalKicks = str(self.totalKicks)
        self.safetyFeatures.saveDiveStatistics(avgDepthData,lowDepthData,tempData,diveTimeData,totalKicks)

    def showPostDiveStatistics(self):
        self.blankScreen()
        avgDepthData = str(round(float(self.depthSum)/float(self.depthReadings),1))
        tempData = str(round(float(self.tempSum)/float(self.depthReadings),1))
        lowDepthData = str(round(self.lowestDepth,1))
        self.safetyFeatures.PostDiveStatistics(self.draw,avgDepthData,lowDepthData,self.totalDiveTime,self.totalKicks,tempData,title="DIVE STATS",diveNumber="")
        self.loadScreen()
        time.sleep(0.3)

    def updateScreen(self,heading,depth,temp,alertCaller):
        #update depth, depthSum, depthReadings, and lowestDepth
        if (self.lowestDepth < depth):
            self.lowestDepth = depth
        self.depthSum = depth+self.depthSum
        self.tempSum = temp + self.tempSum
        self.depthReadings = self.depthReadings + 1
        #Check if we are in the safety stop
        if (depth > self.diveHasBegunLimitMeters and self.safetyStopBoolean == False):
            self.safetyStopBoolean = True
            print("Safety Stop will occur upon resurfacing")
        # check if we have exited the safety stop
        if (self.safetyStopBoolean and depth < self.safetyStopBeginDepth):
            # disable alerts during safety stop
            alertCaller.reset()
            result = self.safetyFeatures.SafetyStop(self.draw,depth)
            self.loadScreen()
            self.blankScreen()
            if (result == -1): # we are no longer in the safety stop
                self.safetyStopBoolean = False
            elif (result == 1): # we have completed the safety stop! Causes to exit loop in main
                print("Completed Safety Stop")
                self.diveComplete = True
            return
        # send alert if it has one to send
        if (alertCaller.hasAlert()):
            myHud.sendAlert(alertCaller.getMessage(),alertCaller.getTime())
        #  if not in safety stop and dive not complte, update the screen
        self.heading = (heading+self.calibrationAdjustment)%360
        curTime = time.time()
        if (abs(depth-self.depth)/(curTime - self.lastTimeScreenUpdated) > 0.1524 ): # Check speed of ascent
            self.NotifyDiverOfAscentSpeed()
            self.lastTimeScreenUpdated = curTime
            self.depth = depth
            return
        self.lastTimeScreenUpdated = curTime
        self.depth = depth
        self.compass.drawCompass(self.heading,self.draw)
        self.depthAndTempMonitor.drawDepthAndTemp(depth,temp,24,self.draw)
        self.kickMonitor.drawKickCounter(self.totalKicks,self.kicks,self.markerSet,24,self.draw)
        self.timeMonitor.drawDiveTime(self.draw)
        self.loadScreen()
        self.blankScreen()
    
    def setCompassMarker(self):
        self.compass.setMarker(self.heading)
        self.markerSet = True

    def clearCompassMarker(self):
        self.compass.clearMarker()
        self.markerSet = False
    
    def sendAlert(self,message,curTime):
        self.alertTime = curTime
        self.alertMessage = message
        self.shouldDisplayAlert = True

def SystemStatus(bno):
    # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
    # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')
    # Print BNO055 software revision and other diagnostic data.
    sw, bl, accel, mag, gyro = bno.get_revision()
    print('Software version:   {0}'.format(sw))
    print('Bootloader version: {0}'.format(bl))
    print('Accelerometer ID:   0x{0:02X}'.format(accel))
    print('Magnetometer ID:    0x{0:02X}'.format(mag))
    print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))
    print('Reading BNO055 data, press Ctrl-C to quit...')

class AlertCaller():
    def __init__(self):
        self.alertTime = 0
        self.alertMessage = ""
        self.shouldDisplayAlert = False

    def createAlert(self,message,curTime):    
        self.alertTime = curTime
        self.alertMessage = message
        self.shouldDisplayAlert = True
    def hasAlert(self):
        return self.shouldDisplayAlert
    def getMessage(self):
        return self.alertMessage
    def getTime(self):
        return self.alertTime
    def reset(self):
        self.alertTime = 0
        self.alertMessage = ""
        self.shouldDisplay = False

def findMaxDiveDataIndex():
    trialNumber = 1
    #path = "C:/Users/Matthew Burruss/Documents/Github/SeniorDesign/SeniorDesignProject/Server/Dives"
    path = "/home/pi/Desktop/SeniorDesign/SeniorDesign/Server/Dives"
    highestIndexFound = False
    while not highestIndexFound:
        filepath = path + "/Dive{0}.csv".format(trialNumber)
        if os.path.isfile(filepath): 
            trialNumber = trialNumber + 1
        else:
            highestIndexFound = True
    return trialNumber-1

def touchDetectorRight(channel):
    global pushButtonPressedRight
    pushButtonPressedRight = True
    time.sleep(0.03)

def touchDetectorLeft(channel):
    global pushButtonPressedLeft
    pushButtonPressedLeft = True
    time.sleep(0.03)

kicks = 0
def KickCounterCommunication():
    global kicks
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    while 1:
        ser.write('1')
        kicks = ser.readline()

pushButtonPressedRight = False
pushButtonPressedLeft = False
if __name__ == '__main__':
    myHud = HUD()
    depthSensor = Sensor()
    alertCaller = AlertCaller()
    bno = BNO055.BNO055(rst=18)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(6, edge=GPIO.FALLING , callback=touchDetectorRight,bouncetime = 20)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(16, edge=GPIO.FALLING , callback=touchDetectorLeft,bouncetime = 20)
    kickThread = Thread(target = KickCounterCommunication)
    kickThread.daemon = True
    kickThread.start()
    if not bno.begin(mode=BNO055.OPERATION_MODE_COMPASS):
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    myHud.calibrateIMU(bno)
    SystemStatus(bno)
    pattern = []                ###########################################
    while(True):
        index = findMaxDiveDataIndex()
        while(myHud.depth<2):
            if (pushButtonPressedRight):
                index = index + 1
                print("Right pressed")
                pattern.append(1)  ###########################################3
                pushButtonPressedRight = False
            if (pushButtonPressedLeft):
                index = index - 1
                print("Left pressed")
                pushButtonPressedLeft = False
                pattern.append(0)                             #############################3
            ###################################################3
            if (len(pattern)>=4):
                print(pattern)
                if (pattern[0]==pattern[2] and pattern[1]==pattern[3] and pattern[0] != pattern[1]):
                    break
                else:
                    empty = []
                    for i in range(len(pattern)-1):
                        empty.append(pattern[i+1])
                    pattern = empty
            ######################################################################333
            index = myHud.displayPreviousDives(index)
            depth, temp = depthSensor.read()
            #myHud.depth = depth
        i = 0
        pattern = [] ################################################################
        mydepth = 10 ################################################################
        while(not myHud.isDiveComplete()):
            myHud.incrementKicks(int(kicks))
            if (pushButtonPressedRight):
                alertCaller.createAlert("MARKER SET",time.time()+3)
                pushButtonPressedRight = False
                myHud.kicks = 0
                myHud.setCompassMarker()
                pattern.append(1)  ############################################33333
            if (pushButtonPressedLeft):
                alertCaller.createAlert("MARKER REMOVED",time.time()+3)
                pushButtonPressedLeft = False
                pattern.append(0)  ###################################################3
                myHud.clearCompassMarker()
            ###################################################3
            if (len(pattern)>=4):
                print(pattern)
                if (pattern[0]==pattern[2] and pattern[1]==pattern[3] and pattern[0] != pattern[1]):
                    mydepth = mydepth - 5
                    pattern = []
                else:
                    empty = []
                    for i in range(len(pattern)-1):
                        empty.append(pattern[i+1])
                    pattern = empty
            ######################################################################333
            heading, roll, pitch = bno.read_euler()
            heading = round(heading)
            if (i%10 == 0):
                depth, temp = depthSensor.read()
                print("Depth: %0.2f"%depth)
                print("Temp: %0.2f"%temp)
                # read in depth
                #depth = float(input())
                i = 0
            i = i+1
            myHud.updateScreen(heading,mydepth,temp,alertCaller)
        myHud.reset() # resets booleans
        myHud.saveDive() # saves dive into memory
        # display post statistics until a button is pressed
        timeout = time.time()
        print("Displaying post dive stats")
        pushButtonPressedLeft = False
        pushButtonPressedRight = False
        while(not pushButtonPressedLeft and not pushButtonPressedRight and timeout + 30 > time.time()):
            myHud.showPostDiveStatistics()
        pushButtonPressedLeft = False
        pushButtonPressedRight = False
        myHud.depth = 0
