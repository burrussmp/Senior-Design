import socket
from ast import literal_eval as make_tuple
import rotation
import threading
from threading import Thread
from datetime import datetime
import csv
import time
from rotation import LinearTracking1
#import signal

server_address = ('10.66.244.204',5001)

def terminate(server_address,sock):
    message = "s"
    message = message.encode()
    sock.sendall(message)

def communicateToServer(server_address,sock):
    message = "\n"
    message = message.encode()
    sock.sendall(message)
    data = sock.recv(128)
    #print(data)
    data_decoded = data.decode()
    data = make_tuple(data_decoded) # (heading, roll, pitch, accX, accY, accZ)
    return data

def plotOrientation():
    print('animating')
    rotation.animateGraph()

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    terminateConnection = False
    thread = Thread(target=plotOrientation)
    timestamps=[]
    heading = roll = pitch = []
    accX = accY = accZ = []
    samples = 0
    acc = (0,0,0)
    # booleans controlling functionality
    DisplayGraphMode = True
    CollectDataMode = False
    Euler = False
    Quaternion = True
    trackMovement = False
    # sample parameters
    NUMBEROFSAMPLES = 2000
    nameOfFile = 'IMUData.csv'
    
    samplerate = 1 # 1 Hz integration of accelerometer
    curTime = time.time()
    nextTick = curTime + 1/samplerate
    data = communicateToServer(server_address,sock)
    if (DisplayGraphMode):
        thread.start()
    if (CollectDataMode):
        csvfile = open(nameOfFile, "w")
    assert(Euler != Quaternion),'Euler and Quaternion boolean cannot equal'
    assert(Euler == False), 'Only use quarternions'
    while (not terminateConnection and samples < NUMBEROFSAMPLES):

        curTime = time.time()
        
        try:
            data = communicateToServer(server_address,sock)
            if (Euler):
                orientation = (data[0],data[1],data[2])
                acc = (data[3],data[4],data[5])
            elif (Quaternion):
                orientation = (data[0],data[1],data[2],data[3])
                acc = (data[4],data[5],data[6])  
            if (DisplayGraphMode):
                if (Euler):
                    rotation.rotationMatrix = rotation.rotate(orientation[0],orientation[1],orientation[2])
                elif (Quaternion):
                    rotation.rotationMatrix = rotation.rotateQuaternion(orientation[0],orientation[1],orientation[2],orientation[3])
                    dt = curTime - nextTick
                    if (trackMovement and curTime > nextTick):
                        nextTick = time.time() + 1/samplerate
                        print('acceleration: x = %0.2f, y = %0.2f, z = %0.2f' %(acc[0],acc[1],acc[2]))
                        LinearTracking1.integrate(acc[0],acc[1],acc[2],function='Riemann')
                        rotation.accx = acc[0]
                        rotation.accy = acc[1]
                        rotation.accz = acc[2]
            if (CollectDataMode):
                samples = samples+1
                print('Sample: %d' %samples)
                heading.append(orientation[0])
                roll.append(orientation[1])
                pitch.append(orientation[2])
                accX.append(acc[0])
                accY.append(acc[1])
                accZ.append(acc[2])
        except Exception as e:
            print(e)
            terminateConnection = True
    terminate(server_address,sock)
    sock.close()
    if (CollectDataMode):
        writer=csv.writer(csvfile)
        writer.writerow(timestamps)
        writer.writerow(heading)
        writer.writerow(roll)
        writer.writerow(pitch)
        writer.writerow(accX)
        writer.writerow(accY)
        writer.writerow(accZ)
        csvfile.close()    