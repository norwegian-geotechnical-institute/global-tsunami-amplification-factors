#!/usr/bin/python

from sct.sio import sio
import time, sys, math, os, json
from sct.Grid1D import Grid1D
#from sct.Wave1D import Wave1D
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.signal import find_peaks

f=sio()
#w=Wave1D(eps=0.001)

def clean():
    cmd="rm -f */.sim_e*"
    os.system(cmd)
    cmd="rm -f */sim_u*"
    os.system(cmd)
    cmd="rm -f */sim_depth"
    #os.system(cmd)
    
def interp(x1,y1,x2,y2,xp):
    g=Grid1D([x1,x2],[y1,y2])
    [x,y]=g.interp_lin([xp])
    return x,y

def leading_peak(teta,eta,eps):
    """locates the time of the first peak (mariogram), returns
    the time and height"""

    peaks, _ = find_peaks(eta)
    found=False
    for i in peaks:
        if eta[i]> eps:
            found=True
            return i,teta[i],eta[i]   
    if not found:
        return 0,0,0
           
def interp_vec(x,y,xp):
    g=Grid1D(x,y)
    [x,y]=g.interp_lin([xp])
    return x,y
       
def tppoints(ampf_depth,xH,H,xdeep,valdeep):
    #find tp points at shoreline and gauge at depth ampf_depth
    tp=[]
    tph=[]
    found0=False
    found_afdepth=False
    i_afdepth=0
    if ampf_depth=='ext_end': 
        #put deep gauge at very end (also if domain is extended with at constant depth)
        print("tppoints - end")
        tp.append(xH[0])
        tph.append(H[0])
    elif ampf_depth=='end':
        tp.append(xdeep)
        tph.append(valdeep)
    elif ampf_depth>=H[0]:
        #find index of depth value above H[0] to avoid location of deepest gauge at 
        #end point of extended constant depth part of profile 
        print("tppoints - ampf_depth>=H[0]", ampf_depth, H[0])
        i=np.argmax(H<H[0])
        tp.append(xH[i])
        tph.append(H[i])

    else:
        #start searching for offshore point from shoreline
        for i in range(len(H)-1,0,-1):
            if not found_afdepth and H[i]>=ampf_depth:
                found_afdepth=True
                [x,y]=interp(H[i],xH[i],H[i-1],xH[i-1],ampf_depth)
                tp.append(y[0])
                tph.append(x[0])
                i_afdepth=i
                break
        print("tppoints - searching from shoreline for offshore point")
            ## if found0 and found50:
        ##     break
    #if still not found, use last point of profile
    if len(tp)==0:
        tp.append(xH[0])
        tph.append(H[0])
        print("tppoints fails -> using last point of profile")
    ######
    # comment this for-loop if last point is used at shoreline:
    ######

    #gauge at shoreline
    istart=i_afdepth-10
    if istart<=0:
        istart=0
    for i in range(istart,len(H),1):
        #stopping at 0.5 m depth at shoreline
        if H[i]<0.0005:
            [x,y]=interp(H[i],xH[i],H[i-1],xH[i-1],0.0005)
            found0=True
            tp.append(y[0])
            tph.append(x[0])
            break


    if not found0:
        print("not found shoreline")
        #using last point
        tp.append(xH[-1])
        tph.append(H[-1])

    return tp,tph

def traveltime(xH,H):
    T=0
    for i in range(len(xH)-1):
        #scaled velocity
        vel=math.sqrt(H[i])
        dx=xH[i+1]-xH[i]
        T+=(dx)/vel
    return T

def find_amp(fil,eps):
    [x,y]=f.read(fil)
    iamp,tamp,amp=leading_peak(x,y,eps)
    #print("tamp,amp",tamp,amp,iamp)
    return amp

def find_max(fil,pol,per):
    [x,y]=f.read(fil)
    #find max between first point above 0.1m (0.0001) and and the distance
    #corresponding to the 0.4 of the traveltime for the wave period
    #both for leading trough and leading peak
    interv=per*0.4*0.1 #half of traveltime for one periode
    #start, y>0.0001
    i=np.argmax(y>0.0001)
    ie=np.argmax(x-x[i]>interv)
    y=y[i:ie]
    x=x[i:ie]
    return y.max()

def find_max_all(fil,pol,per):
    [x,y]=f.read(fil)
    return y.max()

def errorlog(case):
    file=open("error",'a')
    file.write(case+"\n")
    file.close()
    
def domain(y,x):
    #start at shorline side, find first wet point
    #flip arrays (starting at shoreline)
    x=np.fliplr([x])[0]
    y=np.fliplr([y])[0]
    xdist=0
    found=False
    count=0
    while not found and count<4:
        count+=1
        istart=np.argmax(y>0)
        y=y[istart:]
        x=x[istart:]
        iend=np.argmax(y<=0)
        if iend==0:
            iend=len(y)-1
        dist=abs(x[0]-x[-1])
        if dist>5:
            #pick deepest point
            y=y[:iend]
            x=x[:iend]
            
            iend=np.argmax(y)
            y=y[:iend]
            x=x[:iend]
            x-=x[-1]
            found=True
        else:
            y=y[:iend]
            x=x[:iend]
    
    #flip back
    x=np.fliplr([x])[0]
    y=np.fliplr([y])[0]
    return y,x

######################################################################


def run(hpt,ampf_depth,periodes,nr,prof,folder,count,problem,nosim,eps,unitpulse):
    count=int(count)
    foldertime=time.time()
    profnr=str(nr)
    folder=os.path.join(folder,profnr)

    if not nosim:
        if os.path.isdir(folder):
            os.system("rm -rf "+folder)
        os.mkdir(folder)
    
        file=open("error",'w')
        file.write("Following errors in this folder:\n\n")
        file.close()
    
        [xdepth,depth]=f.read(prof)
        #reverse profile and scale: km length and depth
        xdepth=-xdepth+xdepth[-1]
        depth=-depth*0.001
        xdepth=xdepth[::-1]
        depth=depth[::-1]

        #refine depth before removing land-values
        g=Grid1D(xdepth,depth)
        tt=time.time()
        [xdepth,depth]=g.variogrid(dt=0.05)
        
        #only positive values (start from deep part)
        #if not (depth>=0).all():
        #    depth=np.absolute(depth)
        #    case=key+" prof "+str(nr)+" negative values"
        #    problem.append(case)
        #    errorlog(case)
        
        #only positive values (start from deep part)
        no=len(depth)
        cc=0
        ##########################################################AKY
        #cut at first negative value (starting from deeper part)
        while cc<no-1 and depth[cc]>0:
            cc+=1
        
        depth=depth[0:cc]
        xdepth=xdepth[0:cc]
        
        ##########################################################AKY

        #restrict domain til first part of wet area from shorelinepoint
        depth,xdepth=domain(depth,xdepth)

    os.chdir(folder)
    TF=[False,True]
    #TF=[True]
    for neg in TF:
        factors={}  #dict for amp.factors
        for periode in periodes: #[600]: #periodes:
            #change resolution relative to wave periode:
            #checked by convergence tests
            if not nosim:
                if periode<300:
                    #dt=0.05
                    dt=0.25
                elif 300<=periode<=600:
                    #dt=0.1
                    dt=0.5
                else:
                    #dt=0.2
                    dt=1.0

                cpu=time.time()
            
                
                [xbound,bound]=f.read(unitpulse)
                tsc=math.sqrt(0.00981/1) #lengthscale is 1km
                bound*=0.001
                if neg:
                    bound*=-1
                xbound*=tsc*periode
                f.write("bound",xbound,bound)
                boundary="bound"

            
                #find traveltime to shore, tstop=2x
                T=traveltime(xdepth,depth)
                print("Traveltime (scaled)",T)
                xdeep=xdepth[0]
                valdeep=depth[0]
                print("xdeep,valdeep",xdeep,valdeep)

                xdepth_adj=xdepth.copy() #for eventually extending domain
    
                #adjust length of domain for too short domains
                xadd=0
                if tsc*periode > T:
                    #chose extention xadd (length with depth=depth[0])
                    #so that tsc*periode=T
                    xadd=(tsc*periode-T)*math.sqrt(depth[0])
                    xdepth_adj[0]=-xadd
                    xdepth_adj+=xadd
                    xdeep+=xadd
                #update traveltime after eventually extending the domain
                T=traveltime(xdepth_adj,depth)
                print("Traveltime adj (scaled)",T)

                #start and stop of domain
                xs=xdepth_adj[0]
                xe=xdepth_adj[-1]
                
                #find location for offshore gauge (depth=ampf_depth),  and shoreline
                tp,tph=tppoints(ampf_depth,xdepth_adj,depth,xdeep,valdeep)
                print("tp",tp,tph)
                if len(tp)!=2:
                    string=str(hpt)+" "+ str(nr)+" no. of tppoints= "+str(len(tp))
                    problem.append(string)
                    stem="prof%s_"%(profnr)
                    cc=stem+"_T"+str(periode)
                    case=cc+" find_tppoints"
                    errorlog(case)

                    continue
                tplist=[]
                tplist.append(str(tp[0]))
                tplist.append(str(tp[1]))

                #cut domain at shorelin tp:
                xe=float(tp[1])

                #simulation time
                tstop=1.2*T+tsc*periode
                
                tsave=False
                tssave=dt
                count+=1
                        #misc.
            ext="pos"
            if neg:
                ext="neg"
            stem="prof%s_"%(profnr)+ext
            casedir=stem+"_T"+str(periode)

            if not nosim:
                from BQ1D.Boussinesq import Boussinesq as Bouss
                B  = Bouss(boundary=boundary, xs=xs, xe=xe, dt=dt, safety=0.9,
                           tstop=tstop, C=0.9, casename="sim", casedir=casedir,
                           tsave=tsave, tssave=tssave, tplist=tplist, nump=True,
                           etainstab=0.1, radiation=False)


                B.init(xdepth=xdepth_adj,depth=depth)
                B.solve()
                print("after solve",os.getcwd())


            
            #extract amplitude at shoreline and defined depth for offshore point:
            tptfile=casedir+"/sim_e_tpt2"

            max0=find_max_all(tptfile,ext,periode)
            amp0=find_amp(tptfile,eps)
            tptfile=casedir+"/sim_e_tpt1"
            max=find_max_all(tptfile,ext,periode)
            amp=find_amp(tptfile,eps)
            #here is the factor:
            fact=amp0/amp
            maxfact=max0/max
            if abs(maxfact-fact)/fact>0.1:
                ff=folder[-7:]
                cmd="factdiff>0.1 %(fact).6f %(maxfact).6f %(ff)s %(casedir)s \n" %vars()
                print(cmd)
            #factor dumped into dictionary "factors"
            factors[str(periode)]=fact

            if not nosim:
                cpu=time.time()-cpu
                cmd="Run is finnished in %12f seconds" %(cpu)
                print(cmd)
                os.system("rm -f bound")
                out=open(casedir+"/CPU-%.2f"%(cpu),'w')
                out.close()


        out=stem+"_factor"
        file=open(out,'w')

        for per in periodes:
            #try:
            file.write("%d\t%.2f\t%.1f\n"%(int(per),float(factors[str(per)]),float(tph[0])*1000))
            #except:
            #    case=casedir+" write to file"
            #    problem.append(str(hpt)+" "+str(nr)+" compiling factors "+ext+" T"+str(per))
            #    errorlog(case)

        file.close()

    foldertime=time.time()-foldertime
    cmd="All computations in this folder are finnished in %12f seconds" %(foldertime)
    print(cmd)
    out=open("CPU-%.2f"%(foldertime),'w')
    out.close()
    clean()
    os.chdir(os.pardir)
    return problem,count
