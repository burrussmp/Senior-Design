# author: Matthew Burruss
# date: 10/8/2018
# Linear tracking: interface to receive acceleration
# from BNO055 and compute linear movements
import time
import math
from pyquaternion import Quaternion

# Think about saturating the speed
# applying a lowpass filter to address drift for noise

MIN_ACC_MAG = 1.5
MAX_VEL = 0
# tuple functions
def elementWiseTupleSum(t1,t2):
    assert (len(t1) == 3)
    assert (len(t2) == 3)
    return (t1[0]+t2[0],t1[1]+t2[1], t1[2]+t2[2])

def divideTupleByDouble(t1,d):
    assert(len(t1)==3)
    return (t1[0]/d,t1[1]/d,t1[2]/d)
def multiplyTupleByDouble(t1,d):
    assert(len(t1)==3)
    return (t1[0]*d,t1[1]*d,t1[2]*d)
class vectThreeD:
    def __init__(self):
        self.cur = (0,0,0)
        self.prev = (0,0,0)

    def change(self,newValues):
        self.prev = self.cur
        assert(len(newValues)==3)
        self.cur = newValues

    def magnitude(self):
        return math.sqrt(self.cur[0]*self.cur[0] + self.cur[1]*self.cur[1] + self.cur[2]*self.cur[2])
    
    def getprev(self):
        return (self.prev[0], self.prev[1], self.prev[2])
    def integrateRiemann(self,dt,function='left'):
        if (function == 'left'):
            return multiplyTupleByDouble(self.prev,dt)
        if (function == 'right'):
            return multiplyTupleByDouble(self.cur,dt)    
    def integrateTrapezoidal(self,dt):
        return multiplyTupleByDouble(divideTupleByDouble(elementWiseTupleSum(self.cur,self.prev),2),dt)

    def display(self):
        print('x: %0.2f, y: %0.2f, z: %0.2f' %(self.cur[0],self.cur[1],self.cur[2]))

    def getSelf(self):
        return (self.cur[0],self.cur[1],self.cur[2])

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
    
def display():
    print('Acceleration:')
    acc.display()
    print('Velocity:')
    vel.display()
    print('Location:')
    pos.display()
    print("#############")

# x,y,z acceleration vectors (m/s)
# function: either riemann or trapezoidal sums
# sets pos and v vectors to current values
def integrate(x,y,z,function='Riemann'):
    dt = t.dt() # get delta T (s)
    time.sleep(1)
    if (function == 'Riemann'):
        acc.change((x,y,z))
        if (acc.magnitude() < MIN_ACC_MAG):
            acc.change((0,0,0))
        integrateAcc = acc.integrateRiemann(dt,function='left')
        vel.change(elementWiseTupleSum(integrateAcc,vel.cur))
        integrateVel = vel.integrateRiemann(dt,function='left')
        pos.change(elementWiseTupleSum(integrateVel,pos.cur))
    elif (function == 'Trapezoidal'):
        acc.change((x,y,z))
        if (acc.magnitude() < MIN_ACC_MAG):
            acc.change((0,0,0))
        integrateAcc = acc.integrateTrapezoidal(dt)
        vel.change(elementWiseTupleSum(integrateAcc,vel.cur))
        integrateVel = vel.integrateTrapezoidal(dt)
        pos.change(elementWiseTupleSum(integrateVel,pos.cur))
