#!/usr/bin/python

"""
Module with tools for analyzing 1D wave motion.

Example:

>>> from sct.Wave1D import Wave1D as W1D
>>> from sct.sio import sio 
>>> sio=sio()
>>> f=W1D()
>>> x,eta=f.soliton(0.2,h=1.2,type='bouss') #solitary wave profile amp=0.2

>>> print eta[4]
0.0004174903728

>>> [x,eta]=sio.read("Verify/mjo")
Your input is a 1D-file

>>> [xH,H]=sio.read("Verify/mjoH")
Your input is a 1D-file

>>> #info about the leading crest (or crests of a wavetrain):
>>> list=f.front(x,eta,xH,H,no=2)
>>> i=0
>>> for l in list:
...     i+=1
...     print "\ncrest no. ",i
...     for k in l.keys():
...         print "key:\t",k,"\t",l[k]
...

crest no.  1
key:    vel     [454.27199999999999, 0.10174685539360616]
key:    crest   [454.27199999999999, 0.0808064]
key:    depth   [454.27199999999999, 0.54514593600000005]
key:    match   [457.62, 0.0053692000000000002]

crest no.  2
key:    vel     [443.31999999999999, 0.044369720027036437]
key:    crest   [443.31999999999999, 0.0703072]
key:    depth   [443.31999999999999, 0.54147336000000001]
key:    match   [446.01999999999998, 0.0066328400000000001]


>>> print "[x,amp] of first crest:",list[0]['crest']
[x,amp] of first crest: [454.27199999999999, 0.0808064]

>>> xvel,vel=f.eta2vel(x,eta,xH,H) #velocity field (Based on Boussinesq theory)

>>> print vel[30]
-0.0348319561902

"""

from numpy import *
#import numarray
import math,os,scipy
from sct.Grid1D import Grid1D as g1D

class Wave1D:
    def __init__(self,eps=0.0001):
        """self.eps is a truncation parameter for finding leading wavecrests.
        self.eps must be smaller than the amplitude of the crests, but larger
        than other disturbances (noise/small waves etc.)
        Typical value of eps is 10% of the amplitude (or less)"""
        self.eps=eps

    def _test(self):
        import doctest
        doctest.testmod()


    def soliton(self,A,h=1,type='bouss',vel=False,dx=0.1,eps=0.001,x0=0):
        """returns two 1D arrays x,y for a solitary wave of type 'bouss' or
        'kdv', with amplitude A at depth h with maximum at x0=0. The script
        gsol i is used for determining the profile for type='bouss' and is
        developed by Geir K. Pedersen (geirkp@math.uio.no) The profile
        with resolution dx is truncated for eta<eps. If vel=True, the
        velocity profile is returned instead of the surface elevation."""

        ###################################################################
        #10/3-06
        #to be fixed:
        #truncation of kdv-soliton by eps-value, not on a intervall of
        #length 200 ....
        ###################################################################
        
        #scaleing amplitude with depth:
        A/=h

        #find type of solitary wave profile:
        if type=='bouss':
            x,eta=self._soliton_bouss(A,dx,eps)
        elif type=='kdv':
            x,eta=self._soliton_kdv(A,dx,eps)
        else:
            myerror="Only possible choices are 'kdv' and 'bouss'. \
            \nYou tried to use type"
            #raise myerror,type


        #scale with depth
        x  *=h
        eta*=h
        
        #adjust profile with maximum at x0:
        x+=x0

        if vel:
            return self.eta2vel(x,eta,cdepth=h)
        else:
            return x,eta


    def _soliton_bouss(self,A,dx,eps):
        """produces a profile for a solitary wave - Boussinesq. Returns
        two 1D arrays x,eta. The script gsol i developed by Geir K. Pedersen
        (geirkp@math.uio.no)"""

        f=open(".tmp.gsol",'w')
        f.write("%2.5f\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n "
                %(A,'',"linbouss","eta",'',eps,'','',dx,'',''))
        f.close()
        p=os.popen("gsol<.tmp.gsol 2>/dev/null").read().strip().split()
        os.remove(".tmp.gsol")
        #convert output from gsol to float:
        for i in range(len(p)):
            p[i]=float(p[i])
        #fill x and eta
        x=array(p[::2])
        eta=array(p[1:][::2])
        return x,eta


    def _soliton_kdv(self,A,dx,eps):
        """returns a kdv-solitary wave profile x,eta"""
        n=200/dx
        xeta=zeros([n],float)
        eta=zeros([n],float)
        x=-100
        i=0
        while i<n:
            eta[i]=A*(1/(cosh(((3*A)/4)**0.5*x)**2))
            xeta[i]=x
            i+=1
            x+=dx

        return xeta,eta
    
        
    def front(self,xeta,eta,xdepth=False,depth=False,spline=False,\
              dir='right',no=1,cdepth=1):
        
        """finds the leading peaks (tries to locate the first 'no' peaks),
        searching from the direction 'dir' (dir='right' if waves are
        travelling to the right). The amplitude must be larger than self.eps.
        The maximum amplitude is found by the highest node or interp='spline',
        and the depth is either defined by 1D arrays xdepth,depth (may be on an
        another grid than xeta/eta) or by a constant depth set by cdepth.
        The function returns a list of dictionaries.
        The length of the list is 'no' (if there exists that many crests,
        if not the number of peaks extracted is len(list)).
        Each item in the list is a dictionary each with info about the
        corresponding peak:

        dict['crest'] = [x,y] - x=position and y=amplitude of peak
        dict['match'] = [x,y] - matching point used for comparing front/peaks
                                with other solutions such as a solitary
                                wave profile (located at the part of the crest
                                which are facing in the same direction as the
                                waves travel.
        dict['vel']   = [x,y] - y is the velocity at the position x (the peak)
        dict['depth'] = [x,y] - y is the depth below the crest/peak
        

        NB: interpolation using spline for determining the amplitude may
        give unwanted effects - be careful. To be fixed ... !
        
        """

        ###################################################################
        #
        #  10/3-06
        #  to be fixed?:
        #  Mjolnir-tsunami: first trough is below 0 -> add relative depth
        #  to the list?  A=A+trough, depth=depth-trough?
        #
        ##################################################################

        if dir=="left":
            xeta=xeta[::-1]
            eta=eta[::-1]

        n=len(xeta)
        #indexes for max-point of the crests:
        crest=[]
        #indexes for crests. First and last entry is not
        #a trough but rather start and end of the domain
        trough=[]
        epsi=0
        #the first value over eps is the start of a crest/train of peaks:
        for i in range(n-1,0,-1):
            if eta[i]>self.eps: 
                epsi=i
                break
        start=epsi

        trough.append(start)
        #finding the crests/index of top-point:
        for cr in range(no):
            max=-Inf
            min=Inf
            maxi=0
            mini=0
            for i in range(start,0,-1):
                if eta[i]<min:
                    min=eta[i]
                    mini=i
                    max=-Inf
                if eta[i]>max:
                    max=eta[i]
                    maxi=i
                if max-eta[i]>0.1*self.eps:
                    start=i
                    break

            if len(crest)>0:
                if crest[-1]!=maxi:
                    crest.append(maxi)
            else:
                crest.append(maxi)
                
        #finding the indexes of the troughs between the crests
        i=1
        while i<len(crest):
            #find mininum (troughs) of slices between the crests:
            g=g1D(xeta[crest[i]:crest[i-1]],eta[crest[i]:crest[i-1]])
            x,y,index=g.min()
            trough.append(index+crest[i])
            i+=1
        #end-index:
        trough.append(crest[-1]-3)

        #find the velocity, using a slice of the solution between
        #index trough[0] and trough[-1] (suggesting plane wave)
        if isinstance(xdepth,bool):
            cH=1
        else:
            cH=0

        xvel=eta.copy()*0.0
        vel=eta.copy()*0.0
    
        try:
            if isinstance(xdepth,bool):
                #constant depth
                xvel,vel=self.eta2vel(xeta[trough[-1]:trough[0]],\
                                      eta[trough[-1]:trough[0]],cdepth=cdepth)
            else:
                #variable depth defined by arrays xdepth/depth:
                xvel,vel=self.eta2vel(xeta[trough[-1]:trough[0]],\
                                      eta[trough[-1]:trough[0]],xdepth,depth)
        except:
            pass
            
        #make dictionaries with info about the crests/trough:
        #use spline on crests? (make slices of high resolution, find new max):
                     
        list=[] #list with dict
        g=g1D(xeta,eta)
        for i in range(len(crest)):
            dir={}
            start=trough[i+1]
            end=trough[i]

            if spline:    
                x=scipy.mgrid[xeta[start]:xeta[end]:50j]
                x,y=g.interp_spl(x)
                xmax,max,maxi=g.max(x,y)
                dir['crest']=[xmax,max]
            else:
                dir['crest']=[xeta[crest[i]],eta[crest[i]]]
            mi=int((crest[i]+trough[i])/2)
            dir['match']=[xeta[mi],eta[mi]]
            dir['vel']=[xvel[crest[i]-trough[-1]],vel[crest[i]-trough[-1]]]

            #linear interpolation to decide the depth below the crest:
            if cH:   #if constant depth:
                H=cdepth
            else:
                d=g1D(xdepth,depth)
                x,H=d.interp_lin([xeta[crest[i]]])
                H=H[0]
            dir['depth']=[xeta[crest[i]],H]
            list.append(dir)
            
        #print list to screen:
        #for l in list:
        #    for k in l.keys():
        #        print k,l[k]
        return list



    def match_pt(self,xeta,eta,y,dir='right'):
        """returns the first x-value (xeta) where eta=y, searching from
        in the  direction dir. dir='right' means searching from right to
        left (positive xaxis is to the right, negative to the left).
        This function is very handy when a wave is to be plotted and compared
        together with another profile such as a solitary wave profile."""
        
        #if search direction is left:
        if dir!='right':
            eta=eta[::-1]
            xeta=xeta[::-1]
            
        #if not matching the grid find the gridpoints above and below y=y
        for i in range(len(eta)-1,0,-1):
            if eta[i]>y:
                break

        #find the corresponding x-value of for eta=y (linear interpolation)
        rel=(eta[i]-y)/(eta[i]-eta[i+1])
        x=xeta[i]+rel*(xeta[i+1]-xeta[i])

        return x



    def eta2vel(self,xeta,eta,xdepth=[],depth=[],cdepth=1,\
                radial=False,alp=1,eps=1):
        """computes the velocity by using the surface elevation and
        Boussinesq theory.

        xeta, eta    : one dimensional arrays for surface elevation
        xdepth, depth: one dimensional arrays for depth.
        cdepth       : value for constant depth
                       (no need for arrays xdepth and depth)
                       
        
        alp - nonlinear parameter  0 or 1
        eps - dispersive parameter 0 or 1
        
        radial = False => plane wave motion

        returns xvel,vel (one dimensional arrays)
        
        """
        
        sum=0
        nentries=len(eta)
        #intitate matrix/vectors
        A=zeros([nentries,nentries],float)
        b=zeros([nentries])+0.0
        u=zeros([nentries,2],float)
        
        #precompute integral
        integral=zeros([nentries],float)
        if radial:
            for j in range(nentries-2,0,-1):
                try:
                    dr=abs((xeta[j+1]-xeta[j-1])/2.0)
                except:
                    try:
                        dr=abs(xeta[j+1]-xeta[j])
                        
                    except:
                        dr=abs(xeta[j]-xeta[j,0])
                sum+=(eta[j]/xeta[j])*dr*0.5
                integral[j]=sum

        land=0
        constdepth=0
        H=1   #default depth (constant)

        #constant or variable depth:
        if len(xdepth)>0 and len(depth)>0:
            gdepth=g1D(xdepth,depth)
            #print "gdepth, xdepth",xdepth
        else:
            H=cdepth
            constdepth=1

            
        Hn=H  #next
        Ht=H  #this
        Hp=H  #previous

        #boundaries:
        A[0,0]=1
        b[0]=0
        A[nentries-1,nentries-1]=1
        b[nentries-1]=0

        #fill matrix and vector
        for i in range(1,nentries-1):
            dr=abs((xeta[i+1]-xeta[i-1])/2.0)
            if not constdepth:
                #find depth:
                x,Hp=gdepth.interp_lin([xeta[i-1]])
                if Hp<=0:
                    land=1
                x,Ht=gdepth.interp_lin([xeta[i]])
                if Ht<=0:
                    land=1
                x,Hn=gdepth.interp_lin([xeta[i+1]])
                if Hn<=0:
                    land=1
            #fill matrix/vector:
            if land:
                A[i,i-1] = 0
                A[i,i]   = 1 
                A[i,i+1] = 0
                b[i]     = 0
            else:
                A[i,i-1] = float(-math.pow(Hp,2.5)*(1/(dr*dr))*(eps/6.0))
                A[i,i]   = float(math.pow(Ht,0.5)+math.pow(Ht,2.5)\
                                 *(1/(dr*dr))*(eps/3.0))
                A[i,i+1] = float(-math.pow(Hn,2.5)*(1/(dr*dr))*(eps/6.0))
                b[i]     = float(eta[i] - (alp/(4.0*Ht))*eta[i]*eta[i])\
                                 + integral[i]

        #if plane linear hydrostatic: no need for solving matrice...

        #solve system
        #u[:,1]=LinearAlgebra.solve_linear_equations(A, b)
        u[:,1]=linalg.solve(A, b)
        u[:,0]=xeta

        return u[:,0],u[:,1]



        
###############################################################################



    
if __name__=='__main__':

    w=Wave1D(eps=0.01)
    #running doc-test:
    #w._test()

    from sct.sio import sio
    f=sio()
    [xeta,eta]=f.read("Verify/mjo")
    #f.write("wav",xeta,eta)
    [xH,H]=f.read("Verify/mjoH")

    
    #l=w.front(xeta,eta,xdepth=xH,depth=H,spline=0,no=3)
    #x,y=w.soliton(l[0]['crest'][1],h=l[0]['depth'][1],type='bouss',eps=0.001)
    #x,y=w.soliton(0.2,h=1.5,type='bouss',vel=1,eps=0.001)
    #m=w.match_pt(x,y,l[0]['match'][1])
    #x+=l[0]['match'][0]-m

    [x,y]=w.eta2vel(xeta,eta,radial=False)
    f.write("sol",x,y)


    
