import logging
import sys
import time
import os
sys.path.append('/home/pi/Desktop/SeniorDesign/SeniorDesign')
from Adafruit_BNO055 import BNO055
import socket
import shutil
import csv
import datetime
from datetime import datetime

server_address = ('10.66.50.49',5001)
# define data collection lists
temps = ["temps"]
quartx = ["Quartnernion X"]
quarty = ["Quartnernion Y"]
quartz = ["Quartnernion Z"]
quartw = ["Quartnernion W"]
accelx = ["Acceleration X"]
accely = ["Acceleration Y"]
accelz = ["Acceleration Z"]
magnx = ["Magnetometer X"]
magny = ["Magnetometer Y"]
magnz = ["Magnetometer Z"]
acclinx = ["Linear Acceleration X"]
accliny = ["Linear Acceleration Y"]
acclinz = ["Linear Acceleration Z"]
gyrox = ["Gyroscope X"]
gyroy = ["Gyroscope Y"]
gyroz = ["Gyroscope Z"]
timestamps = ["Timestamps"]
syscalib = ["System calibration"]
gyrocalib = ["Gyro calibration"]
accelcalib = ["Acc calibration"]
magcalib = ["Mag calibration"] 
def calibrate(bno):
    sys = accel = 0
    while (sys != 3 or accel != 1 ):
        sys, gyro, accel, mag = bno.get_calibration_status()
        print('Sys: %d Acceleration: %d' %(sys,accel))
    print('Calibrated')

def readBNO055(bno):
    #heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()
    temp_c = bno.read_temp()
    qx,qy,qz,qw = bno.read_quaternion()
    ax,ay,az = bno.read_accelerometer()
    dx,dy,dz = bno.read_gyroscope()
    magx,magy,magz = bno.read_magnetometer()
    accx,accy,accz = bno.read_linear_acceleration()
    syscalib.append(sys)
    gyrocalib.append(gyro)
    accelcalib.append(accel)
    magcalib.append(mag)
    timestamps.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]) # append timestamps and duty cycles
    temps.append(temp_c)
    quartx.append(qx)
    quarty.append(qy)
    quartz.append(qz)
    quartw.append(qw)
    accelx.append(ax)
    accely.append(ay)
    accelz.append(az)
    magnx.append(magx)
    magny.append(magy)
    magnz.append(magz)
    acclinx.append(accx)
    accliny.append(accy)
    acclinz.append(accz)
    gyrox.append(dx)
    gyroy.append(dy)
    gyroz.append(dz)

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

if __name__ == '__main__':
    bno = BNO055.BNO055(rst=18)
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    SystemStatus(bno)
    #sock = createSocket(server_address)
    #print('Waiting for client...')
    #connection, client_address = sock.accept()
    #print('Reading BNO055')
    calibrate(bno)
    input("click any button to begin")
    foo = numberOfSamples = 5000
    count = 0
    csvfile = open("Data.csv", "w")
    while(count<numberOfSamples):
        readBNO055(bno)
        count = count+1
        time.sleep(0.1)
        
    writer=csv.writer(csvfile)
    writer.writerow(timestamps)
    writer.writerow(syscalib)
    writer.writerow(gyrocalib)
    writer.writerow(accelcalib)
    writer.writerow(temps)
    writer.writerow(quartx)
    writer.writerow(quarty)
    writer.writerow(quartz)
    writer.writerow(quartw)
    writer.writerow(accelx)
    writer.writerow(accely)
    writer.writerow(accelz)
    writer.writerow(magnx)
    writer.writerow(magny)
    writer.writerow(magnz)
    writer.writerow(acclinx)
    writer.writerow(accliny)
    writer.writerow(acclinz)
    writer.writerow(gyrox)
    writer.writerow(gyroy)
    writer.writerow(gyroz)
    csvfile.close()    
    print("Copying over to USB Drive")
    newTrialCreated = False
    trialNumber = 1
    while not newTrialCreated:
        newpath = '/media/pi/USB DRIVE/Data{0}.csv'.format(trialNumber)
        if not os.path.isfile(newpath):
             shutil.copy2('/home/pi/Desktop/SeniorDesign/SeniorDesign/Server/Data.csv',newpath)
             newTrialCreated = True
        else:
            trialNumber = trialNumber + 1
    print("Completed copy")
