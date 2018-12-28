import logging
import sys
import time
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
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
import numpy as np
import math
import VUNDT_OLED_Screen

minThreshold = -4.5
maxThreshold = 4
kicks = 0

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

def magnitude(x,y,z):
    return math.sqrt(x*x+ y*y+ z*z)

def readKicks():
    global kicks
    state = "NULL"
    protocol = "NULL"
    acceleration = []
    while 1:
        accx,accy,accz = bno.read_accelerometer()
        accmagNoGrav = magnitude(accx,accy,accz) - 9.8
        acceleration.append(accmagNoGrav)
        state,protocol,kicks = FSM(accmagNoGrav,state,protocol,kicks)
        time.sleep(0.1)

if __name__ == '__main__':
    bno = BNO055.BNO055(rst=18)
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    SystemStatus(bno)
    kickThread = Thread(target=readKicks)
    kickThread.start()
    while 1:
        heading, roll, pitch = bno.read_euler()
        message = str(heading) + ' ' + str(kicks)
        ser.write(str(message))
        time.sleep(1.3)
        print(kicks)
