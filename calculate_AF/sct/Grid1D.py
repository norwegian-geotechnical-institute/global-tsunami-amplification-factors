#!/bin/sh
"""exec" python "$0" "$@"""
"""
Module for manipulating the grid for a given field of values. The module
reads arrays for x and y, and manipulates the grid according to the
parameters and functions called.
"""

import os, sys, math,numpy
import scipy.interpolate as intp




class Grid1D:
    def __init__(self,x=None,y=None):
        #read the arrays:
        if type(x)!='NoneType':
            self.x=x
            self.y=y
#            self.valid_domain()
            
#    def valid_domain(self):
#        """extracts the part of the domain with depth>0. If x[0] is on
#        land, the algorithm will search for the first wet point (start
#        of domain) When this is found, the end of the domain will be
#        either x[-1] or the last wetpoint after the first wet point. In
#        this way we will not have islands in the midle of the domain"""
#        start=False
#        end=False
#        for i in range(len(self.x)):
#            if self.y[i]>0:
#                start=i
#            if start and self.y[i]>0:
#                end=i
#            else:
#                break
#        self.x=self.x[start:end]
#        self.y=self.y[start:end]
#        print self.y
            
            

    def update(self,x,y):
        """exchange the arrays of the instance with new one"""
        self.x=x
        self.y=y

    
    def extrap(self,factor=2):
        """making the grid coarser with an integer factor. factor=2 means
        that every second gridpoint is used in the new
        grid. factor=3 -> every third point is used etc."""


        self.x=self.x[::factor]
        self.y=self.y[::factor]
        
        return self.x,self.y

    

    def interp_spl(self,xnew,x=None,y=None):
        """interpolates values on a new grid based on the grid xnew. xnew
        must be an array (or list) of at least one entry. Field values
        are interpolated using cubic spline. If x=y=None, x=self.x, y=self.y
        is used. The self.x and self.y is updated by the interpolation on
        the grid xnew if len(xnew)>1.
        """
    
        try:
            if x==None or y==None:
                x=self.x
                y=self.y
            
        except:
            pass

        tck=intp.splrep(x,y,s=0)
        ynew=intp.splev(xnew,tck,der=0)

        if len(xnew)==1:
            return xnew,ynew
        else:
            self.update(xnew,ynew)
            return self.x,self.y

    
    def interp_lin(self,xnew,x=None,y=None,outside=True):
        """interpolates values on a new grid based on the grid xnew.
        xnew must be an array of at least one entry. Field values are
        interpolated using linear interpolation. If x=y=None, x=self.x,
        y=self.y is used. The self.x and slef.y is updated by the
        interpolation on the grid xnew if len(xnew)>1.
        """

        #check if new grid is outside or idenstical to the old:

        #return only the overlap between the grids!!!!!!!!!!!!
        ######################################################
        try:
            #if xnew is an array
            xnew=numpy.asarray(xnew)
            ynew=xnew.copy()
            ynew.fill(0.0)
        except: pass
        
        try:
            if x==None and y==None:
                x=self.x
                y=self.y
        except: pass

        f   = intp.interp1d(x,y)

        
        if len(xnew)==1:
            #outside left:
            if xnew[0]<x[0]:
                ynew=[y[0]]
            #outside right:
            elif xnew[0]>x[-1]:
                ynew=[y[-1]]
            else:
                ynew=[f(xnew[0])]

        else:
            #slice of xnew overlapping with x:
            i0,im=self._find_overlap(xnew,x)
            

            yn=f(xnew[i0:im])
            if outside and i0>0:
                ynew[0:i0]=y[0]

            if outside and im<len(xnew)-1:
                ynew[im:-1]=y[-1]

            ynew=numpy.concatenate((ynew[0:i0],yn,ynew[im:]))

        if len(xnew)==1:
            return xnew,ynew
        else:
            self.update(xnew,ynew)
            return self.x,self.y

    def _find_overlap(self,x1,x2):
        """x1 and x2 is 1D grid on array form. The function returns the
        min and max index of array x1 where x1 and x2 is overlapping."""

        i0=0
        im=len(x1)-1
        for i in range(i0,im+1):
            if x1[i]<x2[0]:
                i0=i+1
            if x1[i]>x2[-1]:
                im=i
                break
            else:
                im=len(x1)
        return i0,im

    def bell(self,S=1,center=0,width=1):
        x=self.x.copy()
        return S*math.exp(-(2*(self.x-center)**2)/width**2)


    def smooth(self, steps=1, type=3,S=0,center=0,width=0,weight=0):
        """smoothing data on a 1D uniform grid using 3-pt scheme (type=3)
        or 5 pt scheme (type=5). It is also possible to apply weighted
        smoothing.

        3pt scheme (type=3)
        new(i)=0.25*(old(i-1)+2*old(i)+old(i+1))

        5pt scheme (type=5)
        new(i)=-(1/16)*(old(i-2)+old(i+2)+0.25*(old(i-1)+old(i+1))+(5/8)*old(i)

        Weighting:

        new2(i)=(1-B(i))*old(i)+B(i)*new(i)
        where
        B(i)=S*exp(-(2*(x_i-center)^2)/width^2)  #bellshape


        Updates the data values in array self.y"""

        d=self.y.copy()
        s=d.copy()
        nx=len(self.x)
        #print "Starting smoothing",steps,"steps!"
        B=d.copy() #self.bell(S=S,center=center,width=width)
        B[:]=1
        for no in range(steps):
            d=s
            if type==5:
                #(1-B[2:-2])*d[2:-2]+B[2:-2]*
                s[2:-2]=(-(1.0/16)*(d[:-4]+d[4:])\
                         +0.25*(d[1:-3]+d[3:-1])+(5.0/8)*d[2:-2])
            else:
                #(1-B[1:-1])*d[1:-1]+B[1:-1]*
                s[1:-1]=(0.5*d[1:-1]+0.25*(d[:-2]+d[2:]))
        self.y=s
        return self.x,self.y




    def scale(self,xsc=1,ysc=1):
        """scaleing x,y,z by multiplying the arrays"""
        self.x*=xsc
        self.y*=ysc
        
        return self.x,self.y
        

    def gradient(self,absvalue=True):
        """find the gradient of the non-/uniform field y. Returns x,grad(y)."""
        grad=self.y.copy()
        grad.fill(0.0)
        nx=len(self.x)
        for i in range(1,nx-1):
            grad[i]=(self.y[i+1]-self.y[i-1])/(self.x[i+1]-self.x[i-1])
        if absvalue==True:
            grad=abs(grad)
        self.update(self.x,grad)

        return self.x,self.y

    def max(self,x=None,y=None):
        """returns the maximum field value of y and the
        position in the grid x"""
        try:
            if x==None and y==None:
                x=self.x
                y=self.y
        except: pass

        max=float('-inf')
        for i in range(len(x)):
            if y[i]>max:
                max=y[i]
                maxx=x[i]
                maxi=i

        return maxx,max,maxi

            
    def min(self,x=None,y=None):
        """returns the minimum field value of y and the
        position in the grid x"""
        try:
            if x==None and y==None:
                x=self.x
                y=self.y
        except: pass

        min=float('inf')
        for i in range(len(x)):
            if y[i]<min:
                min=y[i]
                minx=x[i]
                mini=i

        return minx,min,mini




    def zoom(self,x0,xm):
        """shrinking the physical domain of a grid into the
        interval (x0,xm)"""

        #check that x0,xm is inside the original grid:
        
        #find indexes for interval
        i0=0
        nx=len(self.x)
        for i in range(nx):
            if self.x[i]>x0:
                i0=i
                break
        im=nx-1
        for i in range(i0,nx):
            if self.x[i]>xm:
                im=i
                break

        #making slices:
        self.x=self.x[i0:im]
        self.y=self.y[i0:im]
        self.update(self.x,self.y)

        return self.x,self.y

##     def inside(self,x):
##         """checks if point x is inside grid"""
##         if self.x[0]<=x<=self.x[-1]:
##             return True
##         else:
##             return False
    
##     def value_pt(self,x):
##         """returns the y-value of point x"""
##         #check id x,y is outside
##         if self._inside(x,):
##             #interpolated value at x,y
##             ni=0
##             while self.x[ni,0]<=x:
##                 ni+=1
##             iv=ni-1
##             #interpolate values from the y-columns i and i+1:
##             value=self._interp_col(iv,x,y)
##             return value[0]
##         else:
##             print "Point to be evaluated ("+str(x)+","+str(y)+\
##                   ") is outside grid, returning zero."
##             return None
        
##     def replace_value(self,arr,let=None,lat=None,value=-666):
##         """modifies values of self.z if value of same point in
##         'arr' is less than 'let' or larger than 'lat'. The value at this
##         point in 'arr' is then replaced by 'value'. self.z and 'arr' are the
##         values of a field and must be on identical grids.  A typical use of
##         this functionality is to replace surface elevation over land by
##         a value outside the plotting range. 'arr' is then the depth matrix."""
        
##         #may add functionality so that arr2 is interpolated into the
##         #same grid as arr1 if they differ...

##         if let!=None:
##             code="arr[i,j]<%s" % let
##         elif lat!=None:
##             code="arr[i,j]>%s" % lat

##         for i in xrange(self.nx):
##             for j in xrange(self.ny):
##                 if eval(code):
##                     self.z[i,j]=value
        
##         return self.z

    
    def variogrid(self,dt=10,C=1,H=0.01,xs=None,xe=None,x=None,y=None):
        """computes a grid in a variable depth with a constant Courant number,
        C=sqrt(h)*dt/dx. The depth h is interpolated from self.x and self.y if
        x and y (1D arrays for depth) are not given. 

        dt:    timestep
        C:     Courant number (<=1.0)
        H:     critical depth, float. The resolution for h<H is constant
               (=dx at x=H). This avoids infinitesimal dx at the shore (h->0)
        xs/xe: floats, domain of new grid (default: same domain as x/depth
               or self.x/self.y)
        x:     1D array, argument of depth profile (default self.x)
        y:     1D array, values of depth profile. len(y) must equal len(x)
               and each value y[i] correspond to the position x[i].
               (default self.y)

        """
        try:
            if x==None or depth==None:
                x=self.x
                y=self.y
        except: pass


        #adjust xs and xe if the are not given or is outside the depth profile:
        if xs==None or xs<x[0]:
            xs=x[0]
        if xe==None or xe>x[-1]:
            xe=x[-1]

        X     = []         #list of position of the nodes in the new
        Depth = []         #list of correpsonding depth values
        xp    = float(xs)  #position of the new node

        while (xp<=xe):
            X.append(xp)
            #linear interpolation (may instead switch to interp_spl)
            h=self.interp_lin([xp],x,y)[1][0]
            Depth.append(h)
            if h<H:
                h=H
            #next point:
            #print "#%#"*20
            #print xp,h,dt,C,H
            xp+=math.sqrt(h)*float(dt)/float(C)


        nx=len(X)
        #array with the new grid:
        new=numpy.zeros([nx,2],float)

        for i in range(nx):
            new[i,0]=X[i]
            new[i,1]=Depth[i]

        #print info to screen:
        #array holding the gridspacing:
        dx=new[1:-1,0]-new[:-2,0]

        string="\nGrid1D.variogrid:\n"
        string+="The grid has totally "+str(nx)+" points.\n"

        dxmin=self.min(new[:-2,0],dx)
        h=self.interp_lin([dxmin[0]],self.x,self.y)
        string+="Minimum dx = %10.6f at depth = %10.6f and x = %10.6f.\n" %(dxmin[1],h[1][0],dxmin[0])
        dxmax=self.max(new[:-2,0],dx)
        h=self.interp_lin([dxmax[0]],self.x,self.y)
        string+="Maximum dx = %10.6f at depth = %10.6f and x = %10.6f.\n" %(dxmax[1],h[1][0],dxmax[0])

        print(string)
        file=open("variogrid_log",'w')
        file.write(string)
        file.close()

        self.update(new[:,0],new[:,1])
        return self.x,self.y


    def uniformgrid(self,xstart=0,xend=100,dx=0.5):
        """generates a grid with uniform gridspacing. Returns a 1D
        array with xvalues of the grid"""
        n=int((xend-xstart)/dx)+1
        grid=numpy.array(range(n),float)*dx+xstart
        return grid

    
        




            
if __name__ == '__main__':

    
    from sct.sio import sio 

    import scipy,time
    file="sim"
    file="Verify/iotH"
    pd=sio()
    [x,y]=pd.read(file)
    g=Grid1D(x,y)
    print ("x",x)
    print ("y",y)
    #x,y=g.zoom(400,500)
    #X1=x
    #Y1=y
    
#    g.extrap(10)
    #X=g.x
    #Y=g.y
    #x,y=g.smooth(10)
    #x,y=g.zoom(400,500)
    #x,y=g.interp_lin(scipy.array([-1000,430,440,450,460,470,480,1000,10000,20000,200001]),x,y)
    #print x,y
    #pd.write("new1",x,y)
    #x,y=g.interp_spl(X1,x,y)
    #a=numpy.array(numpy.transpose([x,y]))
    #print "a",a
    x,y=g.variogrid(xs=0,xe=700,dt=100,H=0.1,C=1.0)
    #pd.writeDP(x,"DP")
    #x,y=g.gradient(True)
    pd.write("new2",x,y)
