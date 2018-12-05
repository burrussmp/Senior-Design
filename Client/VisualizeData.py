from ast import literal_eval as make_tuple
import rotation
import threading
from threading import Thread
from datetime import datetime
import csv
import time
from rotation import LinearTracking1

nameOfFile = 'C:\Users\Matthew Burruss\Documents\GitHub\SeniorDesign\SeniorDesignProject\Client\calf3.csv'

def plotOrientation():
    print('animating')
    rotation.animateGraph()

if __name__ == '__main__':
    with open(nameOfFile, 'rt') as csvfile:
        reader = csv.reader(csvfile)
        count = 1
        for row in reader:
            if (count == 6 ):
                qx = row
            elif (count == 7):
                qy = row
            elif (count == 8):
                qz = row
            elif (count == 9):
                qw = row
            count = count + 1
    thread = Thread(target=plotOrientation)
    timestamps=[]
    heading = roll = pitch = []
    accX = accY = accZ = []
    samples = 0
    acc = (0,0,0)
    thread.start()
    time.sleep(10)
    for i in range(1,len(qx)):
        rotation.rotationMatrix = rotation.rotateQuaternion(qx[i],qy[i],qz[i],qw[i])
        time.sleep(0.02)