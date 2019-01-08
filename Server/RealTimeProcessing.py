import logging
import sys
import time
import os
import socket
import shutil
import csv
import datetime
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from multiprocessing import Queue

def loadAccelerometer():
    processDataPath = "C:/Users\Matthew Burruss/Documents/MATLAB/Senior Design/calf2.csv"
    # read images in ProcessData.csv and append to input
    with open(processDataPath, 'rt') as csvfile:
        reader = csv.reader(csvfile)
        accx = accy = accz = timestamps = []
        for row in reader:
            if (row[0] == "Timestamps"):
                times = np.array(row[1:])
                for i in range(len(times)):
                    timestamps.append(datetime.datetime.strptime(times[i], "%Y-%m-%d %H:%M:%S.%f"))
            if (row[0] == 'Acceleration X'):
                accx = np.array(row[1:]).astype(np.float)
            elif (row[0] == 'Acceleration Y'):
                accy = np.array(row[1:]).astype(np.float)
            elif (row[0] == 'Acceleration Z'):
                accz = np.array(row[1:]).astype(np.float)
    return accx,accy,accz,timestamps

def magnitude(x,y,z):
    return math.sqrt(x*x+ y*y+ z*z)

"""
Protocol: FOr HIGHTOLOW: HIGH0 to Low to High1 = kick++
for LOWTOHIGH: Low0 to high to low 1 = kick++

"""
class MovingAverage:
    def __init__(self):
        self.myQ = Queue(maxsize=60)
        self.sumElements = 0.0
        self.mean = 0.0
        self.std = 4.5
    def magnitude(x,y,z):
        return math.sqrt(x*x+ y*y+ z*z)
    def addElement(self,element):
        oldElement = 0
        if (self.myQ.full()):
            oldElement = self.myQ.get() # remove from end
        self.myQ.put(element) # add to front
        self.sumElements = element + self.sumElements - oldElement# change sum
        self.mean = self.sumElements/self.myQ.qsize()

    def getStandardDeviation(self):
        #if (not self.myQ.full()): # if the queue is full, we want to calculate std
        #    return -1 # queue must be full
        #else:
        #    if (not self.myQ.empty()): # We know the queue is full and never empty
        index = self.myQ.qsize()
        if (index > 1):    
            var = 0.0
            for i in range(index):
                element = self.myQ.get()
                var = var+math.pow((element - self.mean),2)
                self.myQ.put(element)
            var = var/(self.myQ.qsize()-1.0)
            self.std = math.sqrt(var)
            return self.std
        return -1
        #    else:
        #        return -1

class FSM:
    def __init__(self):
        self.protocol = "NULL"
        self.maxThreshold = 4
        self.minThreshold = -4.5
        self.kickCount = 0
        self.disregardThreshold = 20
        self.state = "NULL"
        self.movingAverage = MovingAverage()
        self.time = time.time()
        self.timeout = 2 #seconds
    def newState(self,accmag):
        if (time.time() - self.time > self.timeout):
            print("kick timeout. Resetting finite state machine")
            self.protocol = "NULL"
            self.maxThreshold = 4
            self.minThreshold = -4.5
            self.state = "NULL"
            self.time = time.time()
            return
        self.movingAverage.addElement(accmag)
        threshold = self.movingAverage.getStandardDeviation()
        if (threshold > 2):
            self.maxThreshold = threshold
            self.minThreshold = -threshold
        if self.protocol == "NULL":
            if accmag > self.maxThreshold:
                self.protocol = "HIGHTOLOW"
                self.state = "HIGH"
            if accmag < self.minThreshold:
                self.protocol = "LOWTOHIGH"
                self.state = "LOW"
        if (accmag > self.disregardThreshold or accmag < -self.disregardThreshold):
            return
        if self.protocol == "HIGHTOLOW":
            if accmag < self.minThreshold and self.state == "HIGH":
                self.state = "LOW"
            if accmag > self.maxThreshold and self.state == "LOW":
                self.state = "HIGH"
                self.kickCount = self.kickCount + 1
                self.time = time.time()
        if self.protocol == "LOWTOHIGH":
            if accmag < self.minThreshold and self.state == "HIGH":
                self.state = "LOW"
                self.kickCount = self.kickCount + 1
                self.time = time.time() 
            if accmag > self.maxThreshold and self.state == "LOW":
                self.state = "HIGH"
    def getKicks(self):
        return self.kickCount

"""
if __name__ == '__main__':
    accx,accy,accz,timestamps = loadAccelerometer()
    magnitudeAcc = []
    fig = plt.figure()
    KickAlgo = FSM()
    prev = timestamps[0]
    for i in range(len(accx)):
        if (i != len(accx)-1):
            diff = timestamps[i+1] - prev
            prev = timestamps[i+1]
        magnitudeAcc.append(magnitude(accx[i],accy[i],accz[i]) - 9.8)
        KickAlgo.newState(magnitude(accx[i],accy[i],accz[i])-9.8)
        kickCount = KickAlgo.getKicks()
        if (magnitudeAcc[i] > 20 or magnitudeAcc[i] < -20):
            magnitudeAcc[i] = 0
    print(kickCount)
    
    ax = fig.add_subplot(111)
    ax.set_xlabel('Sample')
    ax.set_ylabel('m/s^2')
    ax.set_title("Acceleration Magnitude w/out Gravity")
    ax.plot(magnitudeAcc)
    plt.show()

    