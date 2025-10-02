#!/usr/bin/python3

import numpy as np
import netCDF4
#file="/home/sylfest/projects/20220301_Aristotle/global_amp_factors/single_global_set/collect/global_ampf_v01.txt"



def readAF(file):
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



    
 