#!/usr/bin/python3

import subprocess
import netCDF4
import os
import numpy as np
import waveform
from scipy import interpolate

def tms(tms_file: str, af: dict, af_id: str, plot: bool, plot_dir: str, plot_name: str="out"):
    arr=np.loadtxt(tms_file)
    e=arr[:,1]
    time=arr[:,0]


    nonzero=0
    #find id
    print(f"Prosessing mariogram from {tms_file}")
    #extract periode, polarity and height 
    period,hmax,polarity=waveform.waveform(time,e,plot_name,plot_dir,treshold=0.05,plot=plot,quiet=True)

    #extract/interp af
    if period<0.0: 
        period=600.0
    elif period>3600.0:
        period=3600.0

    if period>0.0 and hmax>0.0:
        ampf=interp_ampfact([period],af["periods"],af[af_id][polarity])[0]
    else:
        ampf=1

    #compute MIH
    MIH=ampf*hmax 
    print(f"MIH for mariogram {tms_file} is {MIH:.1f} m with offshore wave amplitude of {hmax:.1f} m, wave period {period:.0f} s and amplification factor {ampf:.2f}.")
    
    return MIH,ampf,hmax


def readAF(file: str):
    #fill a dictionary with  "lon/lat" as key - can substitute with idXXXXX later
    af={}
    periods=np.array([120,200,300,600,1000,1800,3600])
    count=0
    af["periods"]=periods
    for l in open(file,'r').readlines()[1:]:

        l=l.strip().split()
        id,lon,lat=l[0],float(l[1]),float(l[2])
        neg,pos=np.array([float(i) for i in l[4:11]]),np.array([float(i) for i in l[12:19]])
        idll="%(lon).05f/%(lat).05f" %vars()

        #fill in into dictionary
        af[id]={}
        af[idll]=id
        af[id]["id"]=id
        af[id]["lon"]=lon
        af[id]["lat"]=lat
        af[id]["neg"]=neg
        af[id]["pos"]=pos
        count+=1

    return af


def interp_ampfact(inper: float, per: list, af: dict):
    #if period is shorter use T=120
    if inper<per[0]:
        AF=af[0]
    #if period is longer use T=3600
    elif inper>per[-1]:
        AF=af[-1]
    else:
        f = interpolate.interp1d(per,af)
        AF=f([inper])
        AF=AF[0]
    return AF



def computeMIH(ampfact_file: str, ampfact_id: str, tms_file: str, plot: bool=False, plot_name: str="", plot_dir: str="") -> None:

    #read in ampfactors
    af=readAF(ampfact_file)
    # extract amp.factor based on wave forms (polarity and periode) 
    # and offshore surface elevation, and calculate MIH
    results=tms(tms_file, af, ampfact_id, plot, plot_dir, plot_name)   


#####################################################################
#
#  MAIN PART
#
#####################################################################

if __name__=="__main__":
    ampfact="../ampfactors/global_ampf_v04.txt"    #table for amplification factors, either using this global set, or calculating your own table from depth profiles
    tms_file="example_general/tms_00500.txt"       #surface elevation as function of time (sec), two columns ascii file, with time[s] and surf.elev[m]
    ampfact_id="id03700"                           #corresponding id in ampfact-file above
    plot_dir="plot"
    plot_name="check"
    plot=True
    computeMIH(ampfact,ampfact_id, tms_file, plot ,plot_name, plot_dir)