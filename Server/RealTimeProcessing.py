import logging
import sys
import time
import os
import socket
import shutil
import csv
import datetime
from datetime import datetime
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

minThreshold = -4.5
maxThreshold = 4

def loadAccelerometer():
    processDataPath = "C:/Users\Matthew Burruss/Documents/MATLAB/Senior Design/calf1.csv"
    # read images in ProcessData.csv and append to input
    with open(processDataPath, 'rt') as csvfile:
        reader = csv.reader(csvfile)
        accx = accy = accz = []
        for row in reader:
            if (row[0] == 'Acceleration X'):
                accx = np.array(row[1:]).astype(np.float)
            elif (row[0] == 'Acceleration Y'):
                accy = np.array(row[1:]).astype(np.float)
            elif (row[0] == 'Acceleration Z'):
                accz = np.array(row[1:]).astype(np.float)
    return accx,accy,accz

def magnitude(x,y,z):
    return math.sqrt(x*x+ y*y+ z*z)
"""
Protocol: FOr HIGHTOLOW: HIGH0 to Low to High1 = kick++
for LOWTOHIGH: Low0 to high to low 1 = kick++

"""
def FSM(accmag, state,protocol,kickCount):
    # determine protocol if first kick attempt
    if protocol == "NULL":
        if accmag > maxThreshold:
            protocol = "HIGHTOLOW"
            state = "HIGH"
        if accmag < minThreshold:
            protocol = "LOWTOHIGH"
            state = "LOW"
    if (accmag > 20 or accmag < -20):
        return state,protocol,kickCount
    if protocol == "HIGHTOLOW":
        if accmag < minThreshold and state == "HIGH":
            state = "LOW"
        if accmag > maxThreshold and state == "LOW":
            state = "HIGH"
            kickCount = kickCount + 1
    if protocol == "LOWTOHIGH":
        if accmag < minThreshold and state == "HIGH":
            state = "LOW"
            kickCount = kickCount + 1 
        if accmag > maxThreshold and state == "LOW":
            state = "HIGH"
    return state,protocol,kickCount

if __name__ == '__main__':
    accx,accy,accz = loadAccelerometer()
    magnitudeAcc = []
    fig = plt.figure()
    kickCount = 0
    state = "NULL"
    protocol = "NULL"
    for i in range(len(accx)):
        magnitudeAcc.append(magnitude(accx[i],accy[i],accz[i]) - 9.8)
        state,protocol,kickCount = FSM(magnitudeAcc[i],state,protocol,kickCount)
        if (magnitudeAcc[i] > 20 or magnitudeAcc[i] < -20):
            magnitudeAcc[i] = 0
    print(kickCount)

    ax = fig.add_subplot(111)
    ax.set_xlabel('Sample')
    ax.set_ylabel('m/s^2')
    ax.set_title("Acceleration Magnitude w/out Gravity")
    ax.plot(magnitudeAcc)
    plt.show()
