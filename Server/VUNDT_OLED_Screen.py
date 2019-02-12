# @author Matthew Burruss
# @date 12/21/2018
# @description A python script to control a 128x64 OLED Screen

# Developer Notes
# Change when the dive time starts
# Get the selection working between dives before the dive begins
# Get the dive to begin
# Add temperature as a reading
# allow the two to go back and forth
import time
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import math
import subprocess
from VUNDT_OLED_Classes import Compass,DepthGuage,OxygenGauge,KickCounter,DiveTime,HomeScreen,Alert,SafetyFeatures
from KickCountingAlgorithm import FSM
# imports for IMU
import sys
import os
sys.path.append('/home/pi/Desktop/SeniorDesign/SeniorDesign')
from Adafruit_BNO055 import BNO055
import socket
import shutil
from threading import Thread
import threading
import csv
import datetime
from datetime import datetime
#import serial
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
        self.depthMonitor = DepthGuage("metric")
        self.oxygenMonitor = OxygenGauge()
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
        self.diveHasBegunLimitMeters = 8 # depth at which if you go up, safety stop will begin
        self.safetyStopBeginDepth = 6 # meters at which upon rising, safety stop begins
        self.initiateSafetyStop = False # When diver begins to surface, this will be set true.
        self.lastTimeScreenUpdated = time.time()
        self.calibrationAdjustment = 266
        self.lowestDepth = 0
        self.depthSum = 0
        self.depthReadings = 0
        self.showDiveStatistics = False
        #self.displayLogo()
        #for i in range(10):
        #    print("Drawing loading Screen")
        #    self.displayLoadingScreen()

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
        # self.flipImage()
        # self.image.transpose(Image.FLIP_LEFT_RIGHT)

        if (self.shouldDisplayAlert):
            if (self.alertTime > time.time()):
                self.alert.sendAlert(self.alertMessage,45,self.draw)
            else:
                self.shouldDisplayAlert = False
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(0.03)

    def showImage(self,image):
        self.blankScreen()
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(0.03)

    def displayLogo(self):
        self.blankScreen()
        self.image = self.homeScreen.drawLogo()
        self.loadScreen()
        time.sleep(2)
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
        self.loadScreen()
        time.sleep(1)

    def updateScreen(self,heading,kicks,oxygen,depth):
        # Have we completed a dive show the dive statistics for the current dive
        if (self.showDiveStatistics):
            elapsedTime = self.timeMonitor.getTime()
            self.safetyFeatures.PostDiveStatistics(self.depthSum,self.depthReadings,elapsedTime,self.lowestDepth)
            return

        #update depth
        if (self.lowestDepth > depth):
            self.lowestDepth = depth
        self.sumDepth = depth+self.sumDepth
        self.numberDepthReadings = self.numberDepthReadings + 1
        if (depth > self.diveHasBegunLimitMeters and self.safetyStopBoolean == False):
            self.safetyStopBoolean = True
        if (depth < self.safetyStopBeginDepth):
            self.initiateSafetyStop = True

        if (self.safetyStopBoolean and self.initiateSafetyStop):
            result = self.safetyFeatures.SafetyStop(self.draw,depth)
            if (result == -1): # we are no longer in the safety stop
                self.safetyStopBoolean = False
                self.initiateSafetyStop = False
            elif (result == 1): # we have completed the safety stop!
                self.showDiveStatistics = True
            return 
        self.heading = (heading-self.calibrationAdjustment)%360
        curTime = time.time()
        if (abs(depth-self.depth)/(curTime - self.lastTimeScreenUpdated) > 0.1524 ): # Check speed of ascent
            self.NotifyDiverOfAscentSpeed()
            self.lastTimeScreenUpdated = curTime
            self.depth = depth
            return
        self.lastTimeScreenUpdated = curTime
        self.depth = depth
        self.compass.drawCompass(self.heading,self.draw)
        self.depthMonitor.drawDepth(depth,24,self.draw)
        self.oxygenMonitor.drawOxygen(oxygen,34,self.draw)
        self.kickMonitor.drawKickCounter(kicks,24,self.draw)
        self.timeMonitor.drawDiveTime(self.draw)
        self.loadScreen()
        self.blankScreen()
    
    def setCompassMarker(self):
        self.compass.setMarker(self.heading)

    def clearCompassMarker(self):
        self.compass.clearMarker()
    
    def sendAlert(self,message,curTime):
        self.alertTime = curTime
        self.alertMessage = message
        self.shouldDisplayAlert = True
        if (self.alertMessage == "MARKER SET"):
            self.setCompassMarker()
    
    def flipImage(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

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

def touchDetector(channel):
    global pushButtonPressed
    GPIO.remove_event_detect(16)
    pushButtonPressed = True
    GPIO.add_event_detect(16, edge=GPIO.FALLING , callback=touchDetector,bouncetime = 20)

pushButtonPressed = False
if __name__ == '__main__':
    myHud = HUD()
    alertCaller = AlertCaller()
    bno = BNO055.BNO055(rst=18)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(16, edge=GPIO.FALLING , callback=touchDetector,bouncetime = 20)
    if not bno.begin(mode=BNO055.OPERATION_MODE_COMPASS):
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    #myHud.calibrateIMU(bno)
    SystemStatus(bno)
    oxygenLevels = 200
    depthLevel = 0
    heading = 0
    i = 0
    while(True):
        i = i + 1
        if (pushButtonPressed):
            alertCaller.createAlert("MARKER SET",time.time()+3)
            pushButtonPressed = False
        heading, roll, pitch = bno.read_euler()
        heading = round(heading)
        if (i%20==0):
            depthLevel = depthLevel+1
        if(i%45 == 0):
            oxygenLevels = oxygenLevels - 25
        if (alertCaller.hasAlert()):
                myHud.sendAlert(alertCaller.getMessage(),alertCaller.getTime())
                alertCaller.reset()
        myHud.updateScreen(heading,0,oxygenLevels,depthLevel)
