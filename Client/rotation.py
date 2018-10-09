# author: Matthew Burruss
# date: 10/7/2018
# author: Matthew Burruss
# date: 10/7/2018
import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pyquaternion import Quaternion
import LinearTracking

#Quaternion = [1 0 0 0];     # output quaternion describing the Earth relative to the sensor
# identity rotation matrix
#rotationMatrix = [[1 , 0 ,  0],
#                 [0,  1 ,  0],
#                 [0,  0,  1]]
rotationMatrix = Quaternion([1,0,0,0])
accx = accy = accz = 0
# rotate based on header, pitch, and roll
# arguments in degrees
def rotate(header,pitch,roll):
    a = math.radians(header)
    b = math.radians(pitch)
    y = math.radians(roll)
    Rz = np.matrix([[math.cos(a),-math.sin(a),0], \
              [math.sin(a), math.cos(a),0], \
              [0, 0, 1]])
    Ry = np.matrix([[math.cos(b),0,math.sin(b)], \
              [0, 1, 0], \
              [-math.sin(b), 0, math.cos(b)]])
    Rx = np.matrix([[1,0,0], \
              [0, math.cos(y), -math.sin(y)], \
              [0, math.sin(y), math.cos(y)]])
    rotate = np.dot(np.dot(Rz,Ry),Rx)
    return rotate

# rotate based on quaternion
def rotateQuaternion(x,y,z,w):
    my_quaternion = Quaternion(w=w, x=x, y=y, z=z)
    return my_quaternion

# animateGraph()
# Description: creates a dynamic matrix
def animateGraph():
    global rotationMatrix,accx,accy,accz
    global fig
    fig = plt.figure()
    points = np.array([[-2.5, -1.5, -0.5],
                    [-2.5, 1.5, -0.5 ],
                    [2.5, 1.5, -0.5],
                    [2.5, -1.5, -0.5],
                    [-2.5, -1.5, 0.5],
                    [-2.5, 1.5, 0.5 ],
                    [2.5, 1.5, 0.5],
                    [2.5, -1.5, 0.5]])
    yaxis = np.array([[0,1.5,0],
                    [0,4.5,0]])
    xaxis = np.array([[2.5,0,0],
                    [5.5,0,0]])
    zaxis = np.array([[0,0,0.5],
                    [0,0,3.5]])

    ax = fig.add_subplot(211, projection='3d')
    ax2 = fig.add_subplot(212, projection='3d')
    # animate()
    def animate(i):
        #try:
        Z = np.zeros((8,3))
        xaxisR = np.zeros((2,3))
        yaxisR = np.zeros((2,3))
        zaxisR = np.zeros((2,3))
        #print(rotationMatrix)
        for i in range(8): 
            #Z[i,:] = np.dot(points[i,:],rotationMatrix)
            Z[i,:] = rotationMatrix.rotate((points[i,0],points[i,1],points[i,2]))
        for i in range(2):
            #xaxisR[i,:] = np.dot(xaxis[i,:],rotationMatrix)
            #yaxisR[i,:] = np.dot(yaxis[i,:],rotationMatrix)
            #zaxisR[i,:] = np.dot(zaxis[i,:],rotationMatrix)
            xaxisR[i,:] = rotationMatrix.rotate((xaxis[i,0],xaxis[i,1],xaxis[i,2]))
            yaxisR[i,:] = rotationMatrix.rotate((yaxis[i,0],yaxis[i,1],yaxis[i,2]))
            zaxisR[i,:] = rotationMatrix.rotate((zaxis[i,0],zaxis[i,1],zaxis[i,2]))
        
        LinearTracking.integrate(accx,accy,accz)
        ax.clear()
        r = [-1,1]

        X, Y = np.meshgrid(r, r)
        # plot vertices
        ax.scatter3D(Z[:, 0], Z[:, 1], Z[:, 2])
        ax.plot3D(xaxisR[:,0],xaxisR[:,1],xaxisR[:,2],color='r')
        ax.plot3D(yaxisR[:,0],yaxisR[:,1],yaxisR[:,2],color='g')
        ax.plot3D(zaxisR[:,0],zaxisR[:,1],zaxisR[:,2],color='b')

        pos = LinearTracking.pos.getSelf()

        ax2.scatter3D(pos[0],pos[1],pos[2])
        ax.set_xlim(-5,10)
        ax.set_ylim(-5,10)
        ax.set_zlim(-5,10)
        # list of sides' polygons of figure
        verts = [[Z[0],Z[1],Z[2],Z[3]],
        [Z[4],Z[5],Z[6],Z[7]], 
        [Z[0],Z[1],Z[5],Z[4]], 
        [Z[2],Z[3],Z[7],Z[6]], 
        [Z[1],Z[2],Z[6],Z[5]],
        [Z[4],Z[7],Z[3],Z[0]], 
        [Z[2],Z[3],Z[7],Z[6]]]

        # plot sides
        ax.add_collection3d(Poly3DCollection(verts, facecolors='cyan', linewidths=1, edgecolors='k', alpha=.25))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        #except:
        #    print('Exception')
    plt.grid(True)
    #plt.subplots_adjust(hspace = 1,wspace = 0.6)
    ani = animation.FuncAnimation(fig, animate, interval=1)
    plt.show()
