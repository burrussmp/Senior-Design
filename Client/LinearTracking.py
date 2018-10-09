# author: Matthew Burruss
# date: 10/8/2018
# Linear tracking: interface to receive acceleration
# from BNO055 and compute linear movements
import time
import math
from pyquaternion import Quaternion
class vectThreeD:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.xprev = 0
        self.yprev = 0
        self.zprev = 0

    def magntidue(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def change(self,newValues):
        self.xprev = self.x
        self.yprev = self.y
        self.zprev = self.z
        self.x = newValues[0]
        self.y = newValues[1]
        self.z = newValues[2]
    def getprev(self):
        return (self.xprev, self.yprev, self.zprev)

    def integrateRiemann(self,dt,function='left'):
        if (function == 'left'):
            return (dt*self.xprev + self.xprev,
            dt*self.yprev + self.yprev,
            dt*self.zprev + self.zprev)
        if (function == 'right'):
            return (dt*self.x + self.xprev, 
            dt*self.y + self.yprev, 
            dt*self.z + self.zprev)
            
    def integrateTrapezoidal(self,dt):
        return (self.xprev+dt*(self.xprev+self.x)/2,\
               self.yprev+dt*(self.yprev+self.y)/2, \
               self.zprev+dt*(self.zprev+self.z)/2)
    def display(self):
        print('x: %0.2f, y: %0.2f, z: %0.2f' %(self.x,self.y,self.z))

    def getSelf(self):
        return (self.x,self.y,self.z)
class timeValue:
    def __init__(self):
        self.value = time.time()
    def dt(self):
        dt = time.time() - self.value
        self.value = time.time()
        return dt

acc = vectThreeD()
vel = vectThreeD()
pos = vectThreeD()

t = timeValue()
def elementWiseTupleSum(t1,t2):
    assert (len(t1) == 3)
    assert (len(t2) == 3)
    return (t1[0]+t2[0],t1[1]+t2[1], t1[2]+t2[2])

def display():
    print('Acceleration:')
    acc.display()
    print('Velocity:')
    vel.display()
    print('Location:')
    pos.display()

# x,y,z acceleration vectors (m/s)
# function: either riemann or trapezoidal sums
# sets pos and v vectors to current values
def integrate(x,y,z,function='Riemann'):
    dt = t.dt() # get delta T (s)
    if (function == 'Riemann'):
        acc.change((x,y,z))
        vel.change(elementWiseTupleSum(acc.integrateRiemann(dt,function='right'),vel.getprev()))
        pos.change(elementWiseTupleSum(vel.integrateRiemann(dt,function='right'),pos.getprev()))
    elif (function == 'Trapezoidal'):
        acc.change((x,y,z))
        vel.change(elementWiseTupleSum(acc.integrateTrapezoidal(dt),vel.getprev()))
        pos.change(elementWiseTupleSum(vel.integrateTrapezoidal(dt),pos.getprev()))

