import logging
import sys
import time
sys.path.append('/home/pi/Desktop/SeniorDesign/SeniorDesign')
from Adafruit_BNO055 import BNO055
import socket
import math
server_address = ('10.66.50.49',5001)

def calibrate(bno):
    sys = accel = 0
    while (sys != 3 or accel != 1 ):
        sys, gyro, accel, mag = bno.get_calibration_status()
        print('Sys: %d Acceleration: %d' %(sys,accel))
    print('Calibrated')

def readBNO055(bno,Quaternion):
    heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out.
    """
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))
    """
    x,y,z = bno.read_linear_acceleration()
    accx,accy,accz = bno.read_accelerometer()
    #print(accx)
    #print(accy)
    #print(accz)
    #time.sleep(0.5)
    # Orientation as a quaternion:
    if (Quaternion):
        qx,qy,qz,qw = bno.read_quaternion()
        return (qx,qy,qz,qw,x,y,z)
    else:
        heading, roll, pitch = bno.read_euler()
        return (heading,roll,pitch,x,y,z)
    # Sensor temperature in degrees Celsius:
    #temp_c = bno.read_temp()
    # Magnetometer data (in micro-Teslas):
    #x,y,z = bno.read_magnetometer()
    # Gyroscope data (in degrees per second):
    #x,y,z = bno.read_gyroscope()
    # Accelerometer data (in meters per second squared):
    #x,y,z = bno.read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    #x,y,z = bno.read_linear_acceleration()
    # Gravity acceleration data (i.e. acceleration just from gravity--returned
    # in meters per second squared):
    #x,y,z = bno.read_gravity()
    # Sleep for a second until the next reading)
    #return (qx,qy,qz,qw,x,y,z)

def createSocket(server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(1)
    return sock

# initializeConnection()
# Summary: Creates initial TCP/IP connection with client and correctly sets miny and maxy (range of steering values)
# Parameter: sock => connection to accept
def communicateToClient(sock,message):
    data = connection.recv(16)
    data_decoded = data.decode()
    if (data_decoded == 's'):
        sock.close()
        print('Done.')
        exit(0)
    #print(data_decoded)
    message = str(message)
    connection.sendall(message)

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

def getAverage(mArray):
    sum = 0.0
    for i in range(len(mArray)):
        sum = sum+mArray[i]
    return sum/float(len(mArray))
if __name__ == '__main__':
    bno = BNO055.BNO055(rst=18)
    if not bno.begin(BNO055.OPERATION_MODE_COMPASS):
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    #SystemStatus(bno)
    #sock = createSocket(server_address)
    #print('Waiting for client...')
    #connection, client_address = sock.accept()
    #print('Reading BNO055')
    #calibrate(bno)
    sum = 0.0
    while(True):
        accx,accy,accz= bno.read_accelerometer()
        accmag = math.sqrt(accx*accx+accy*accy+accz*accz)
        print(accmag-9.8)
        #error = 0.37869642
        #error = 0.32
        #print(accmag-error)
        #afterError = accmag - error
        #sum = sum + afterError
        #print(sum)
        time.sleep(0.1)
    """
    averageError = []
    for i in range(10):
        mags = []
        count = 0.0
        while(count < 100):
            accx,accy,accz= bno.read_linear_acceleration()
            accmag = math.sqrt(accx*accx+accy*accy+accz*accz)
            mags.append(accmag)
            time.sleep(0.1)
            count = count+1.0
        avg = getAverage(mags)
        print(avg)
        averageError.append(avg)
    print(getAverage(averageError))
    """
    # booleans
    #Quaternion = True # if false, collect euler angles
    #while(True):
    #    message = readBNO055(bno,Quaternion)
    #    communicateToClient(sock,message)
