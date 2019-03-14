from PIL import Image, ImageDraw, ImageFont
import time
import math
import csv
import os
import datetime as datetime
import numpy as np
path = "/home/pi/Desktop/SeniorDesign/SeniorDesign/Server/"
#path = "C:/Users/Matthew Burruss/Documents/Github/SeniorDesign/SeniorDesignProject/Server/"
#import matplotlib.pyplot as plt
#import matplotlib.animation as anim
#import zmq
class CompassUnit:
    def __init__(self,kind,text,heading):
        self.kind = kind
        self.text = text
        self.heading = heading
        if (kind == "cardinal"):
            self.font = ImageFont.truetype(path+"NirmalaB.ttf",10)
        else:
            self.font = ImageFont.truetype(path+"slkscr.ttf",8)
        (self.mwidth,self.height) = self.font.getsize(self.text)
        self.width=21
    def drawMe(self,x,y,draw):
        if (self.kind == "cardinal"):
            draw.line(((x+self.width/2,y),(x+self.width/2,y+2)),fill=255)
            draw.text((x+self.width/2-self.mwidth/2, y), self.text, font=self.font, fill=255)
        else:
            draw.line(((x+self.width/2,y),(x+self.width/2,y+1)),fill=255)
            draw.text((x+self.width/2-self.mwidth/2, y+2), self.text, font=self.font, fill=255)
    def getWidth(self):
        return self.width
    def getHeading(self):
        return self.heading

class Compass:
    def __init__(self):
        self.compassUnits = dict()
        self.font = ImageFont.truetype(path+"slkscre.ttf",8)
        # create cardinal units
        self.compassUnits[0] = CompassUnit("cardinal","N",0)
        self.compassUnits[180] = CompassUnit("cardinal","S",180)
        self.compassUnits[90] = CompassUnit("cardinal","E",90)
        self.compassUnits[270] = CompassUnit("cardinal","W",270)
        self.compassUnits[315] = CompassUnit("cardinal","NW",315)
        self.compassUnits[45] = CompassUnit("cardinal","NE",45)
        self.compassUnits[225] = CompassUnit("cardinal","SW",225)
        self.compassUnits[135] = CompassUnit("cardinal","SE",135)
        self.hasMarker = False
        # create the rest of the parts
        for i in range(0,360,15):
            if (i%45 != 0):
                self.compassUnits[i] = CompassUnit("",str(i),i)
    def setMarker(self,heading):
        self.marker = heading
        self.hasMarker = True
    def clearMarker(self):
        self.hasMarker = False
    def drawCompass(self,heading,draw,widthOfScreen=128):
        nearest15 = (math.ceil(heading / 15.0)) * 15 # next highest 15
        lowerBound = (nearest15-45)%360 # whatever the next highest is -45
        width = 21
        dX = math.ceil((nearest15-heading)*(width/(15.0-1.0)))
        X = -width-width/2+1
        Y = 0
        head = -1
        if (self.hasMarker):
            firstIndex = (lowerBound-15)%360
            distanceFromFirst = (self.marker-firstIndex)%360
            pixelsFromFirst = math.ceil(distanceFromFirst*(width/15.0))
            y = 14
            draw.rectangle((X+dX+width/2+pixelsFromFirst-1,y-3,X+dX+width/2+pixelsFromFirst+1,y-3), outline=255, fill=255)
            draw.line(((X+dX+width/2+pixelsFromFirst,y),(X+dX+width/2+pixelsFromFirst,y-4)),fill=255)
        while (X < widthOfScreen):
            index = ((lowerBound) + head*15)%360
            self.compassUnits[index].drawMe(X+dX,Y,draw)
            X = X + width
            head = head + 1
        # draw marker if necessary
        center = widthOfScreen/2
        #draw arrow key
        draw.polygon([(center-2,14), (center+2, 14), (center,12)], fill = 255)
        (width,height) = self.font.getsize(str(heading))
        # draw lines and heading indicator
        Y = 16
        draw.text((center-width/2, Y), str(heading), font=self.font, fill=255)
        draw.line(((0,Y+height/2),(center-width/2-2,Y+height/2)),fill=255)
        draw.line(((center+width/2+2,Y+height/2),(128,Y+height/2)),fill=255)

class DepthAndTempGuage:
    def __init__(self,kind):
        self.font = ImageFont.truetype(path+"slkscr.ttf",8)
        self.text = ""
        self.kind = kind # either metric or empirical
    # depth collected in meters
    def drawDepthAndTemp(self,depth,temp,y,draw):
        if (self.kind == "empirical"):
            depthInFeetRounded = round(depth*3.28084,2)
            depthText = str(depthInFeetRounded) + "ft"
        elif (self.kind == "metric"):
            depthInMetersRounded = round(depth,2)
            depthText = self.text+str(depthInMetersRounded) + "m"
        (width,height) = self.font.getsize(depthText)
        draw.text((128-width-2, y), depthText, font=self.font, fill=255)
        tempText = self.text + str(round(temp,2)) + "C"
        (width,height) = self.font.getsize(tempText)
        draw.text((128-width-2, y+10), tempText, font=self.font, fill=255)
    def changeToMetric(self):
        self.kind = "metric"
    def changeToEmpirical(self):
        self.kind = "empirical"

class OxygenGauge:
    def __init__(self):
        self.font = ImageFont.truetype(path+"slkscr.ttf",8)
        self.text = ""
    def drawOxygen(self,oxygen,y,draw):
        oxygenText = self.text + str(oxygen) + " psi"
        (width,height) = self.font.getsize(oxygenText)
        draw.text((128-width-2, y), oxygenText, font=self.font, fill=255)

class KickCounter:
    def __init__(self):
        self.font = ImageFont.truetype(path+"slkscr.ttf",8)
        self.text = "Total Kicks: "
    def drawKickCounter(self,totalKicks,kicks,markerSet,y,draw):
        if (markerSet):
            kickText = "Kicks: " + str(kicks)
            draw.text((2, y), kickText, font=self.font, fill=255)
        else:
            kickText = self.text + str(totalKicks)
            draw.text((2, y), kickText, font=self.font, fill=255)
class DiveTime:
    def __init__(self):
        self.font = ImageFont.truetype(path+"slkscr.ttf",8)
        self.text = "Time: "
        self.elapsedTime = 0
    def startTimer(self):
        self.start = time.time()

    def getTime(self):
        return self.elapsedTime

    def drawDiveTime(self,draw):
        self.elapsedTime = time.time()-self.start
        timeText = self.text + str(int(self.elapsedTime/60)) + ":" + str(int(self.elapsedTime%60))
        (width,height) = self.font.getsize(timeText)
        x = 8
        # center = 64 - width/2 # center
        draw.line(((0,64-height-2),(128,64-height-2)),fill=255)
        draw.text((x, 64-height-1), timeText, font=self.font, fill=255)
class Alert:
    def __init__(self):
        self.font = ImageFont.truetype(path+"slkscr.ttf",8)
    def sendAlert(self,alertText,y,draw):
        draw.text((2, y), alertText, font=self.font, fill=255)
class HomeScreen:
    def __init__(self):
        self.font = ImageFont.truetype(path+"NirmalaB.ttf",20)
        self.font2 = ImageFont.truetype(path+"slkscr.ttf",10)
        self.title = "VUNDT"
        self.calibratingText = "Calibrating"
        self.counter = 0
        self.image = Image.open(path+'Logo.png').resize((128, 64), Image.ANTIALIAS).convert('1')
    def drawLoadScreen(self,draw):
        (width,height) = self.font.getsize(self.title)
        # x = 64-width/2 # center
        draw.line(((0,20-height/2-2),(128,20-height/2-2)),fill=255)
        draw.text((64-width/2, 20-height/2), self.title, font=self.font, fill=255)
        draw.line(((0,20+height/2+6),(128,20+height/2+6)),fill=255)
        (width,height) = self.font2.getsize(self.calibratingText + "."*self.counter)
        draw.text((64-width/2, 64-height-2), self.calibratingText + "."*self.counter, font=self.font2, fill=255)
        self.counter = (self.counter+1)%4
    def drawLogo(self):
        return self.image
class SafetyFeatures:
    def __init__(self):
        self.font = ImageFont.truetype(path+"NirmalaB.ttf",15)
        self.font2 = ImageFont.truetype(path+"NirmalaB.ttf",12)
        self.font3 = ImageFont.truetype(path+"Nirmala.ttf",10)
        self.font4 = ImageFont.truetype(path+"Nirmala.ttf",8)
        self.font5 = ImageFont.truetype(path+"slkscr.ttf",8)          
        self.safetyTimerStart = 0
        self.safetyStopTime = 5*60 #seconds ##########################################################################################
    def AscendingorDescendingTooQuickly(self,draw):
        (width,height) = self.font.getsize("SLOW")
        draw.text((64-width/2, 20-height/2), "SLOW", font=self.font, fill=255)
        (width,height) = self.font.getsize("ASCENT/DESCENT")
        draw.text((64-width/2, 40-height/2), "ASCENT/DESCENT", font=self.font, fill=255)
    def SafetyStop(self,draw,depth):
        # if depth below 9 we are not in the safety stop
        if (depth > 9):
            return -1
        if (self.safetyTimerStart == 0):
            self.safetyTimerStart = time.time()
        df = self.safetyStopTime + (self.safetyTimerStart - time.time())
        if (df < 0 or depth <1): # we have completed the safety stop
            return 1
        timeText = "Time: " + str(int(df/60)) + ":" + str(int(df%60))
        (width,height) = self.font2.getsize("SAFETY STOP")
        draw.text((64-width/2, 0), "SAFETY STOP", font=self.font2, fill=255)
        draw.line(((0,15),(128,15)),fill=255)
        (width,height) = self.font3.getsize(timeText)
        draw.text((2, 64-height -1), timeText, font=self.font3, fill=255)
        # draw depth diagram
        draw.line(((65,25),(100,25)),fill=255)
        draw.line(((65,55),(100,55)),fill=255)
        (width,height) = self.font4.getsize("4m")
        draw.text((65-width, 25-height/2-1), "4m", font=self.font4, fill=255)
        (width,height) = self.font4.getsize("6m")
        draw.text((65-width, 55-height/2-1), "6m", font=self.font4, fill=255)
        # draw arrow
        if (depth > 6 or depth < 4):
            if (depth > 6):
                depthWarning = "Too low!"
                depthNormalized = 1
            if (depth < 4):
                depthWarning = "Too high!"
                depthNormalized = 0
            (width,height) = self.font3.getsize(depthWarning)
            draw.text((2, 32-height-1), depthWarning, font=self.font3, fill=255)
        else:
            depthNormalized = (depth-4.0)/(6.0-4.0)
        y_denormalized = depthNormalized*(55-25)+25
        depthText = str(round(depth,1))
        (width,height) = self.font5.getsize(depthText)
        draw.text((106, y_denormalized-height/2-1), depthText, font=self.font5, fill=255)
        draw.line(((102,y_denormalized),(105,y_denormalized)),fill=255)
        draw.line(((102,y_denormalized+2),(102,y_denormalized-2)),fill=255)
        return 0
    # Displays: Avg depth, total dive time, lowest depth, temperature
    # need to add temperature
    def PostDiveStatistics(self,draw,avgDepthData,lowDepthData,diveTimeData,totalKicks,tempData="30",title="DIVE STATS",diveNumber=""):
        #Print Dive Number if it exists
        if (diveNumber != ""):
            numberStr = "#" + str(diveNumber)
            (width,height) = self.font2.getsize(numberStr)
            draw.text((2, 0), numberStr, font=self.font2, fill=255)
            draw.line(((0,15),(128,15)),fill=255)
        # Print Title
        (width,height) = self.font2.getsize(title)
        draw.text((64-width/2, 0), title, font=self.font2, fill=255)
        draw.line(((0,15),(128,15)),fill=255)
        # Print average Depth
        avgDepthTitle = "Avg Depth (m): "
        #avgDepthData = str(round(float(depthSum)/float(depthReadings),1))
        draw.text((2, 16), avgDepthTitle, font=self.font5, fill=255)
        draw.text((90, 16), avgDepthData, font=self.font5, fill=255)
        # Print lowest Depth
        lowDepthTitle = "Max (m):"
        #lowDepthData = str(round(lowestDepth,1))
        draw.text((2, 25), lowDepthTitle, font=self.font5, fill=255)
        draw.text((90, 25), lowDepthData, font=self.font5, fill=255)
        # Print temperature
        tempTitle = "Temp (C):"
        #tempData = "30"
        draw.text((2, 34), tempTitle, font=self.font5, fill=255)
        draw.text((90, 34), tempData, font=self.font5, fill=255)        
        # Print total dive time
        diveTimeTitle = "Dive Time:"
        #diveTimeData = str(int(totalTimeElapsed/60)) + ":" + str(int(totalTimeElapsed%60))
        draw.text((2, 43), diveTimeTitle, font=self.font5, fill=255)
        draw.text((90, 43), diveTimeData, font=self.font5, fill=255)
        # Print total kicks
        totalKickTitle = "Total Kicks:"
        #diveTimeData = str(int(totalTimeElapsed/60)) + ":" + str(int(totalTimeElapsed%60))
        draw.text((2, 52), totalKickTitle, font=self.font5, fill=255)
        draw.text((90, 52), str(totalKicks), font=self.font5, fill=255)
        return
    # inputs are strings
    def saveDiveStatistics(self,avgDepth,lowestDepth,temp,diveTime,totalKicks):
        # store datao
        data = []
        date = datetime.datetime.today().strftime('%m/%d/%y')
        data.append(date)
        data.append(avgDepth)
        data.append(lowestDepth)
        data.append(temp)
        data.append(diveTime)
        data.append(totalKicks)
        #path = "C:/Users/Matthew Burruss/Documents/Github/SeniorDesign/SeniorDesignProject/Server/Dives"
        path = "/home/pi/Desktop/SeniorDesign/SeniorDesign/Server/Dives"
        newTrialCreated = False
        trialNumber = 1
        while not newTrialCreated:
            filepath = path + "/Dive{0}.csv".format(trialNumber)
            if not os.path.isfile(filepath): 
                newTrialCreated = True
            else:
                trialNumber = trialNumber + 1
        csvfile = open(filepath, "w")
        writer=csv.writer(csvfile)
        writer.writerow(data)
        csvfile.close()
    # returns the dive data
    # ["date","avgerage depth","lowestdepth","temperature","divetime"]
    def readPreviouslyStoredDive(self,indexToRead):
        if (indexToRead <1):
            indexToRead = 1 
        #path = "C:/Users/Matthew Burruss/Documents/Github/SeniorDesign/SeniorDesignProject/Server/Dives"
        path = "/home/pi/Desktop/SeniorDesign/SeniorDesign/Server/Dives"
        trialFound = False
        trialNumber = indexToRead
        while not trialFound:
            filepath = path + "/Dive{0}.csv".format(trialNumber)
            if os.path.isfile(filepath): 
                trialFound = True
            else:
                trialNumber = trialNumber -1
            if (trialNumber == 0):
                return -1,0
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if (len(row)!=0):
                    data = row
        return data,trialNumber
    # displays a dive based on index
    def displayPreviousDiveData(self,draw,indexToRead):
        data,indexFound = self.readPreviouslyStoredDive(indexToRead) # Data = ["date","avgerage depth","lowestdepth","temperature","divetime"]
        # first dive collected
        if (data == -1):
            self.displayNoDiveData(draw)
        else:
            self.PostDiveStatistics(draw,avgDepthData=data[1],lowDepthData=data[2],diveTimeData=data[4],tempData=data[3],totalKicks = data[5],title=data[0],diveNumber=indexFound)
        return indexFound

    def displayNoDiveData(self,draw):
        title = "NO DATA"
        (width,height) = self.font2.getsize(title)
        draw.text((64-width/2, 0), title, font=self.font2, fill=255)
        draw.line(((0,15),(128,15)),fill=255)
        text = "Device will begin"
        (width,height) = self.font2.getsize(text)
        draw.text((64-width/2, 20), text, font=self.font5, fill=255)
        text = "automatically"
        (width,height) = self.font2.getsize(text)
        draw.text((64-width/2, 30), text, font=self.font5, fill=255)
        text = "upon descent"
        (width,height) = self.font2.getsize(text)
        draw.text((64-width/2, 40), text, font=self.font5, fill=255)
"""
# get an image
image = Image.new('1', (128, 64))
# get a font

# get a drawing context
draw = ImageDraw.Draw(image)
padding = -2
top = padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
img = None
    
compass = Compass()
depthMonitor = DepthAndTempGuage("metric")
oxygenMonitor = OxygenGauge()
kickMonitor = KickCounter()
timeMonitor = DiveTime()
timeMonitor.startTimer()
homeScreen = HomeScreen()
safetyFeatures = SafetyFeatures()
alert = Alert()
depth = 3
oxygen = 200
kicks = 0
minutes = 0
index = 5
# socket stuff
IP = "10.66.204.238"
Port = "5001"
context = zmq.Context()
sock = context.socket(zmq.REQ)
sock.connect("tcp://%s:%s" %(IP,Port))
for i in range(1000):
    draw.rectangle((0,0,128,64), outline=0, fill=0)
    #if (i == 0):
     #   safetyFeatures.AscendingorDescendingTooQuickly(draw)
        #img.set_data(image)
     #   plt.pause(2)
    if (i>10):
        depth = depth+0.2
    if (i% 10 == 0 and i != 0 and i < 31):
        index = index - 1
    if (i > 30):
        depth = depth - 0.4
        if (i % 10 == 0):
            index = index + 1
    if (i > 40):
        depth = 5
    #safetyFeatures.SafetyStop(draw,depth)
    #safetyFeatures.PostDiveStatistics(title="DIVE STATS",avgDepthData="33.3",lowDepthData="40",tempData="30",diveTimeData="0:48")
    index = safetyFeatures.displayPreviousDiveData(draw,index)
    #img.set_data(image)
    plt.pause(0.03)
    img = plt.imshow(image)
    img.set_data(image)
    frame = np.asarray(image)
    data = cv2.imencode('.jpg', frame)[1].tostring()
    sock.send(data.encode())
    message = sock.recv()
    print(message.decode())
    plt.draw()
goBackward = False
alerting = False
count = 0
for i in range(0,720,1):
    if (goBackward):
        count = i
        break
    draw.rectangle((0,0,128,64), outline=0, fill=0)
    if i == 0:
        compass.setMarker(15)
        img = plt.imshow(image)
    else:
        compass.drawCompass(i%360,draw)
        depthMonitor.drawDepth(depth,22,draw)
        oxygenMonitor.drawOxygen(oxygen,32,draw)
        kickMonitor.drawKickCounter(kicks,22,draw)
        timeMonitor.drawDiveTime(draw)
        if (i == 6):
            alerting = True
        if (alerting):
            alert.sendAlert("Descending too fast!",45,draw)
        if (i == 15 ):
            alerting = False
        if (i%20==0):
            depth = depth+1
        if(i%45 == 0):
            oxygen = oxygen - 25
        if(i%3==0):
            kicks = kicks+1
        if(i==57):
            compass.setMarker(57)
            goBackward = True
        img.set_data(image)
    plt.pause(0.03)
    plt.draw()

for i in range(count,0,-1):
    draw.rectangle((0,0,128,64), outline=0, fill=0)
    compass.drawCompass(i%360,draw)
    depthMonitor.drawDepth(depth,22,draw)
    oxygenMonitor.drawOxygen(oxygen,32,draw)
    kickMonitor.drawKickCounter(kicks,22,draw)
    timeMonitor.drawDiveTime(draw)
    if (i%20==0):
        depth = depth+1
    if(i%45 == 0):
        oxygen = oxygen - 25
    if(i%3==0):
        kicks = kicks+1
    if(i==57):
        compass.setMarker(57)
        goBackward = True
    img.set_data(image)
    plt.pause(0.1)
    plt.draw()
"""
