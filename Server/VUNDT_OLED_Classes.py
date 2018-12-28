from PIL import Image, ImageDraw, ImageFont
import time
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import math

class CompassUnit:
    def __init__(self,kind,text,heading):
        self.kind = kind
        self.text = text
        self.heading = heading
        if (kind == "cardinal"):
            self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\NirmalaB.ttf",10)
        else:
            self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
        (self.mwidth,self.height) = self.font.getsize(self.text)
        self.width=18
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
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscre.ttf",8)
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
        nearest15 = int(math.ceil(heading / 15.0)) * 15
        lowerBound = (nearest15-45)%360
        width = 21
        dX = int(float(abs(heading-nearest15)/15.0)*width)
        #print(X)
        X = -21
        #X = 0
        Y = 0
        head = 0
        drawnMarker = False
        while (X < widthOfScreen):
            index = ((lowerBound) + head*15)%360
            if (self.hasMarker):
                indexNext = ((lowerBound) + (head+1)*15)%360
                if (indexNext > self.marker and index <= self.marker and not drawnMarker):
                    drawnMarker = True
                    addMe = int((self.marker-index)*(21/15))
                    if (index != self.marker):
                        addMe = addMe + 25
                    else:
                        addMe = addMe + 21
                    x = X + addMe
                    y = 14
                    draw.rectangle((x+dX,y-3,x+2+dX,y-3), outline=255, fill=255)
                    draw.line(((x+dX+1,y),(x+dX+1,y-4)),fill=255)
            self.compassUnits[index].drawMe(X+dX+13,Y,draw)
            X = X + width
            head = head + 1
        #draw arrow key
        center = widthOfScreen/2
        draw.polygon([(center-2,14), (center+2, 14), (center,12)], fill = 255)
        (width,height) = self.font.getsize(str(heading))
        # draw lines and heading indicator
        Y = 16
        draw.text((center-width/2, Y), str(heading), font=self.font, fill=255)
        draw.line(((0,Y+height/2),(center-width/2-2,Y+height/2)),fill=255)
        draw.line(((center+width/2+2,Y+height/2),(128,Y+height/2)),fill=255)

class DepthGuage:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
        self.text = "Depth: "
    def drawDepth(self,depth,y,draw):
        depthText = self.text+str(depth) + "m"
        (width,height) = self.font.getsize(depthText)
        draw.text((128-width-2, y), depthText, font=self.font, fill=255)

class OxygenGauge:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
        self.text = "O2: "
    def drawOxygen(self,oxygen,y,draw):
        oxygenText = self.text + str(oxygen) + " psi"
        (width,height) = self.font.getsize(oxygenText)
        draw.text((128-width-2, y), oxygenText, font=self.font, fill=255)

class KickCounter:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
        self.text = "Kicks: "
    def drawKickCounter(self,kicks,y,draw):
        kickText = self.text + str(kicks)
        draw.text((2, y), kickText, font=self.font, fill=255)

class DiveTime:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
        self.text = "Dive Time: "
    def drawDiveTime(self,time,draw):
        timeText = self.text + str(time) + " minutes"
        (width,height) = self.font.getsize(timeText)
        draw.line(((0,64-height-2),(128,64-height-2)),fill=255)
        draw.text((64-width/2, 64-height-1), timeText, font=self.font, fill=255)
class Alert:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",8)
    def sendAlert(self,alertText,y,draw):
        draw.text((2, y), alertText, font=self.font, fill=255)
class HomeScreen:
    def __init__(self):
        self.font = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\NirmalaB.ttf",20)
        self.font2 = ImageFont.truetype("C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Server\slkscr.ttf",10)
        self.title = "VUNDT"
        self.calibratingText = "Calibrating"
        self.counter = 0
        self.image = Image.open('C:\Users\Matthew Burruss\Documents\Senior Design\Logo.png').resize((128, 64), Image.ANTIALIAS).convert('1')
    def drawLoadScreen(self,draw):
        (width,height) = self.font.getsize(self.title)
        draw.line(((0,20-height/2-2),(128,20-height/2-2)),fill=255)
        draw.text((64-width/2, 20-height/2), self.title, font=self.font, fill=255)
        draw.line(((0,20+height/2+6),(128,20+height/2+6)),fill=255)
        (width,height) = self.font2.getsize(self.calibratingText + "."*self.counter)
        draw.text((64-width/2, 64-height-2), self.calibratingText + "."*self.counter, font=self.font2, fill=255)
        self.counter = (self.counter+1)%4
    def drawLogo(self):
        return self.image

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
depthMonitor = DepthGuage()
oxygenMonitor = OxygenGauge()
kickMonitor = KickCounter()
timeMonitor = DiveTime()
homeScreen = HomeScreen()
alert = Alert()
depth = 0
oxygen = 200
kicks = 0
minutes = 0

for i in range(10):
    draw.rectangle((0,0,128,64), outline=0, fill=0)
    if (i == 0):
        img = plt.imshow(homeScreen.drawLogo())
        plt.pause(8)
    else:
        homeScreen.drawLoadScreen(draw)
        img.set_data(image)
        plt.pause(0.5)
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
        timeMonitor.drawDiveTime(minutes,draw)
        if (i%5 == 0):
            minutes = minutes +1
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
    plt.pause(0.1)
    plt.draw()

for i in range(count,0,-1):
    draw.rectangle((0,0,128,64), outline=0, fill=0)
    compass.drawCompass(i%360,draw)
    depthMonitor.drawDepth(depth,22,draw)
    oxygenMonitor.drawOxygen(oxygen,32,draw)
    kickMonitor.drawKickCounter(kicks,22,draw)
    timeMonitor.drawDiveTime(minutes,draw)
    if (i%5 == 0):
        minutes = minutes +1
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
