#!/usr/bin/python3

import subprocess
import netCDF4
import os
import numpy as np
from scipy import interpolate

def tms_cpp(ncfile: str, ctr_file: str, af: dict):
    results={}
    results["nonzero"]=0
    #output from cpp-program for waveform extraction from HySEA is a txt file:
    wavef=f"{ncfile}.offshore.txt"    
    # read the results into dictionary both the combination of output from cpp (waveforms) and controlfile (with correct id)
    # 1. read in control_dict: ctr_dict with key as the counting number of lines
    count=0
    ctr_dict={}
    with open(ctr_file,'r') as f:
        for line in f:
            if count>0:
                l=line.strip().split()
                id,lon,lat=l[0],l[1],l[2]
                ctr_dict[count]={}
                ctr_dict[count]["id"]=id
                ctr_dict[count]["lon"]=lon
                ctr_dict[count]["lat"]=lat
            count+=1

    # 2. read in waveform dict, fill dict results with calculated MIH from AF (key is global id, idXXXXX)
    tmscount=0
    nonzero=0
    with open(wavef,'r') as f:
        for line in f:
            l=line.strip().split()
            if tmscount>0:
                lon,lat,depth,max,min,period,polarity,return_code=float(l[1]),float(l[2]),float(l[3]),float(l[4]),float(l[5]),float(l[6]),int(l[7]),float(l[8])
                keyll="%(lon).05f/%(lat).05f" %vars()   
                if polarity==-1:
                    polarity="neg"
                elif polarity==1:
                    polarity="pos"

                id=ctr_dict[tmscount]["id"]
                nonzero=0
                if return_code > 1:
                    #get AF-factor
                    ampf=interp_ampfact(period,af["periods"],af[id][polarity])
                    #correct with Greens law assuming AF is calculated from 50 m isobath. 
                    max *= pow(depth/50, 0.25)
                    #compute MIH
                    MIH = ampf*max
                    nonzero=1
                elif return_code == 1 and abs(max)<0.05 and depth>0:
                    #this is points in sea with max below treshold (0.05m)
                    max=MIH=0.0
                    nonzero=1
                else:
                    #rest (either points on land or strange wave signal)
                    MIH = -1
                    max = -1
                    period = -1
                    nonzero=0
                results[id]={}
                results[id]["count"]=tmscount
                results[id]["lon"]=lon
                results[id]["lat"]=lat
                results[id]["MIH"]=MIH
                results[id]["key"]=keyll
                results[id]["period"]=period
                results[id]["hmax"]=max
                results["nonzero"]+=nonzero
            tmscount+=1
    return results

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



def computeMIH(af: dict, tms_file: str, tms_id_file: str, results_file: str) -> None:

    #dictionary for ampfacts is in af
    
    ###################################################################
    #
    #   MAIN LOOP OVER ALL TIMESERIES, CALCULATE MIH FROM AF
    #
    ###################################################################

    results=tms_cpp(tms_file,tms_id_file,af)   
    nonzero=results["nonzero"]
    print("nonzero:",nonzero)

    #####################################################################
    #
    #  Save results to a file (columnwise)
    #
    #####################################################################

    fil=open(results_file,'w')

    fil.write("#id lon lat MIH hmax period\n")
    for k in results.keys():
        if k!="nonzero":
            lonp=af[k]["lon"]
            latp=af[k]["lat"]
            MIH=results[k]["MIH"]
            hmax=results[k]["hmax"]
            per=results[k]["period"]
            fil.write("%(k)s %(lonp)f %(latp)f %(MIH).2f %(hmax).2f %(per).0f\n" %vars())

    fil.close()
    print(f"The computed MIH for mariograms from HySEA (file: {tms_file}) is saved in {results_file}")

#####################################################################
#
#  MAIN PART
#
#####################################################################

if __name__=="__main__":
    ampfact="../ampfactors/global_ampf_v04.txt" 
    af=readAF(ampfact)          #corresponding factors for POIs 
    tms_file="example_HySEA/result_ts.nc"                 #output from HySEA, location of POIs from ampfact
    tms_id_file="example_HySEA/result_ts.nc_id.txt"       #input id file, location of POIs in HySEA with corresponding id
    out_results="example_HySEA/calculated_MIH_HySEA.txt"  #name of outputfile
    computeMIH(af,tms_file, tms_id_file, out_results)