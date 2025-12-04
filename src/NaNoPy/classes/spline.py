from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math
import cmath
import platform
import numpy as np

class spline:
    """Spline class for generating a spline trhough given points"""
    def __init__(self,xs,ys,loop):
        self.x = np.array(xs)
        self.y = np.array(ys)            

        n = len(self.x)

        # matrix = np.array(shape=(n,n),dtype = np.float32)
        # resultsy = np.array(shape=(n,1),dtype = np.float32)
        # resultsx = np.array(shape=(n,1),dtype=np.float32)

        self.loop = loop

        if loop:
            segments = self.x.size 
            
            matrix = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
            matrix[0,n-1] = 1
            matrix[n-1,0] = 1

            

            resultsx = 3 * (np.roll(self.x,-1,0) - np.roll(self.x,1,0))
            resultsy = 3 * (np.roll(self.y,-1,0) - np.roll(self.y,1,0))
        else:

            segments = self.x.size - 1

            matrix = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
            matrix[0,0] = 2
            matrix[n-1,n-1] = 2

            

            resultsx = 3 * (np.roll(self.x,-1,0) - np.roll(self.x,1,0))
            resultsx[0] = 3* (self.x[1] - self.x[0])
            resultsx[n-1] = 3 * (self.x[n-1]-self.x[n-2])
            resultsy = 3 * (np.roll(self.y,-1,0) - np.roll(self.y,1,0))
            resultsy[0] = 3* (self.y[1] - self.y[0])
            resultsy[n-1] = 3 * (self.y[n-1]-self.y[n-2])

            

        matrix_inv = np.linalg.inv(matrix)
        kx = np.matmul(matrix_inv,resultsx)
        ky = np.matmul(matrix_inv,resultsy)

        

        self.ay = self.y
        self.by = ky
        self.cy = (3 * ((np.roll(self.y,-1,0)-self.y)) - (2*(ky)) - np.roll(ky,-1,0))
        self.dy = (2 * (self.y - np.roll(self.y,-1,0))) + ky + np.roll(ky,-1,0)
        self.ax = self.x
        self.bx = kx
        self.cx = (3 * ((np.roll(self.x,-1,0)-self.x)) - (2*(kx)) - np.roll(kx,-1,0))
        self.dx = (2 * (self.x - np.roll(self.x,-1,0))) + kx + np.roll(kx,-1,0)
        
        

        for i in range(0,segments):       
            samples = max( abs(self.x[i]-self.x[(i+1)%self.x.size]) , abs(self.y[i]-self.y[(i+1)%self.y.size])  )
            samples = math.ceil(samples*2.5)
            t = np.linspace(0,1,num=samples)
                        
            tempx = (self.ax[i] + self.bx[i]*t + self.cx[i]*(t*t) + self.dx[i]*(t*t*t))
            tempy = (self.ay[i] + self.by[i]*t + self.cy[i]*(t*t) + self.dy[i]*(t*t*t))
            tempdy = (self.by[i] + (2*self.cy[i]*t) + (3*self.dy[i]*(t*t)))
            tempdx = (self.bx[i] + (2*self.cx[i]*t) + (3*self.dx[i]*(t*t)))
            tempdydx = (tempdy/tempdx)

            if i == 0:
                outx = tempx
                outy = tempy
                outdydx = tempdydx
            else:
                outx = np.concatenate((outx,tempx), axis=0)
                outy = np.concatenate((outy,tempy), axis=0)
                outdydx = np.concatenate((outdydx,tempdydx), axis=0)
        
        

        self.splinex = outx
        self.spliney = outy
        self.splinedydx = outdydx

        if loop:
            self.getInsidePix()

    def getInsidePix(self):
        inds = self.spliney.argsort()
        sortedy = self.spliney[inds]
        sortedx = self.splinex[inds]
        boundingbox = [np.min(self.splinex),np.min(self.spliney),np.max(self.splinex),np.max(self.spliney)]
        sortedy = sortedy - boundingbox[1]
        sortedx = sortedx - boundingbox[0]
        minx = np.full(math.ceil(boundingbox[3]-boundingbox[1])+1,math.ceil(boundingbox[2]-boundingbox[0])+1)
        maxx = np.zeros(math.ceil(boundingbox[3]-boundingbox[1])+1)

        for j in range(len(sortedy)):
            i = math.ceil(sortedy[j])
            if sortedx[j] < minx[i]:
                minx[i] = sortedx[j]
            if sortedx[j] > maxx[i]:
                maxx[i] = sortedx[j]
            
             

        for i in range(len(minx)):
            if i == 0:
                self.insidex = (np.arange(math.floor(minx[i]),math.ceil(maxx[i]))+boundingbox[0])
                self.insidey = (np.full(math.ceil(maxx[i])-math.floor(minx[i]),(i+boundingbox[1])))                
                
            else:
                self.insidex = np.concatenate((self.insidex,(np.arange(math.floor(minx[i]),math.ceil(maxx[i]))+boundingbox[0])),axis=0)
                self.insidey = np.concatenate((self.insidey,(np.full(math.ceil(maxx[i])-math.floor(minx[i]),(i+boundingbox[1])))),axis=0)

    def getInside(self,x,y):

        


        splncx = np.average(self.ax)
        splncy = np.average(self.ay)
        

        #draw line trhough given point and center, extend beyond bounding box

        if splncx < x:
            x1 = splncx
            x2 = x
            y1 = splncy
            y2 = y
        if splncx >= x:
            x1 = x
            x2 = splncx
            y1 = y
            y2 = splncy
        
        dx = x2-x1
        dy = y2-y1

        if dx == 0 and dy == 0:
            return True
        
        
        numberofsegments = len(self.ax)
            
        if self.loop:
            n = numberofsegments
        else:
            n = numberofsegments-1
        
        valid_intercepts = []
        all_intercepts = []

        for segno in range(n):
            if dx != 0: 
                
                E = dy/dx
                F = y1 - (x1*E)

                a = self.ax[segno] 
                b = self.bx[segno] 
                c = self.cx[segno]
                d = self.dx[segno]
                e = self.ay[segno]
                f = self.by[segno]
                g = self.cy[segno]
                h = self.dy[segno]
                i = E
                j = F

                #redefine an a+bx+cx2+dx2 formula

                a = ((i*a)+j)-e
                b = (i*b)-f
                c = (i*c)-g
                d = (i*d)-h

            if dx == 0:
                a = self.ax[segno] - x1
                b = self.bx[segno] 
                c = self.cx[segno]
                d = self.dx[segno] 

                    
            #solve cubic for real values 
            #https://medium.com/@mephisto_Dev/solving-cubic-equation-using-cardanos-method-with-python-9465f0b92277
            #https://math.stackexchange.com/questions/243961/find-x-given-y-in-a-cubic-function

            p = (3*d*b - c**2) / (3*d**2)
            q = (2*c**3 - 9*d*c*b + 27*d**2*a) / (27*d**3)
            delta = (q**2 / 4 + p**3 / 27)

            # determine number and type of roots
            if delta > 0:  # one real and two complex roots
                    
                u = (-q/2 + cmath.sqrt(delta))
                v = (-q/2 - cmath.sqrt(delta))

                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                v_regular = v ** (1./3) if v >= 0 else -(-v)**(1./3)
                v_cbrt = math.cbrt(v) 

                xx1 = u_regular + v - c / (3*d)
                xx2 = -(u_regular + v_regular)/2 - c / (3*d) + (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx3 = -(u_regular + v_regular)/2 - c / (3*d) - (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx4 = u_cbrt + v_cbrt - c / (3*d)
                xx5 = -(u_cbrt + v_cbrt)/2 - c / (3*d) + (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                xx6 = -(u_cbrt + v_cbrt)/2 - c / (3*d) - (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                # print("One real root and two complex roots:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2)
                # print("x3 = ", xx3)
            elif delta == 0:  # three real roots, two are equal
                u = (-q/2)
                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                xx1 = ((2*u_regular) - c) / (3*d)
                xx2 = ((-u_regular) - c) / (3*d)
                xx3 = ((-u_regular) - c) / (3*d)
                xx4 = ((2*u_cbrt) - c) / (3*d)
                xx5 = ((-u_cbrt) - c) / (3*d)
                xx6 = ((-u_cbrt) - c) / (3*d)
                # print("Three real roots, two are equal:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2.real)
                # print("x3 = ", xx3.real)
            else:  # three distinct real roots
                u = (-q/2 + cmath.sqrt(delta))
                v = (-q/2 - cmath.sqrt(delta))
                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                v_regular = v ** (1./3) if v >= 0 else -(-v)**(1./3)
                v_cbrt = math.cbrt(v) 

                xx1 = u_regular + v - c / (3*d)
                xx2 = -(u_regular + v_regular)/2 - c / (3*d) + (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx3 = -(u_regular + v_regular)/2 - c / (3*d) - (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx4 = u_cbrt + v_cbrt - c / (3*d)
                xx5 = -(u_cbrt + v_cbrt)/2 - c / (3*d) + (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                xx6 = -(u_cbrt + v_cbrt)/2 - c / (3*d) - (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                # print("Three distinct real roots:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2.real)
                # print("x3 = ", xx3.real)

            if delta > 0:
                all_intercepts.append([segno,xx1.real])
                if 0 <= xx1.real <= 1:
                    tint = xx1.real
                    valid_intercepts.append([segno,tint])
                all_intercepts.append([segno,xx4.real])
                if 0 <= xx4.real <= 1:
                    tint = xx4.real
                    valid_intercepts.append([segno,tint])
            if delta <= 0:
                all_intercepts.append([segno,xx1.real])
                all_intercepts.append([segno,xx2.real])
                all_intercepts.append([segno,xx3.real])
                if 0 <= xx1.real <= 1:
                    tint = xx1.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx2.real <= 1:
                    tint = xx2.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx3.real <= 1:
                    tint = xx3.real
                    valid_intercepts.append([segno,tint])
                all_intercepts.append([segno,xx4.real])
                all_intercepts.append([segno,xx5.real])
                all_intercepts.append([segno,xx6.real])
                if 0 <= xx4.real <= 1:
                    tint = xx4.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx5.real <= 1:
                    tint = xx5.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx6.real <= 1:
                    tint = xx6.real
                    valid_intercepts.append([segno,tint])
        
        countbefore = 0

        

        truevalids = []

        for i in range(len(valid_intercepts)):
            segmentno = valid_intercepts[i][0]
            tintercept = valid_intercepts[i][1]

            xint = self.ax[segmentno]+(self.bx[segmentno]*tintercept)+(self.cx[segmentno]*(tintercept**2))+(self.dx[segmentno]*(tintercept**3))
            yint = self.ay[segmentno]+(self.by[segmentno]*tintercept)+(self.cy[segmentno]*(tintercept**2))+(self.dy[segmentno]*(tintercept**3))
            valid_intercepts[i].append(xint)
            valid_intercepts[i].append(yint)

            if  math.isclose(yint , (E*xint) + F):

                truevalids.append([valid_intercepts[i],xint,yint])

                if xint < x:
                    countbefore += 1
        
        

        if countbefore%2 == 1:
            return True
        else:
            return False