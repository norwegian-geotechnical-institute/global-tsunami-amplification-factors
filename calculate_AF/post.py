#!/usr/bin/python

import matplotlib.pyplot as plt
#from sct.sio import sio
import time,os,re,sys
import numpy as np


##########################################################
##########################################################

simdir="/home/sgl/projects/global-tsunami-amplification-factors/calculate_AF/sim"

##########################################################
##########################################################

periodes=[120,200,300,600,1000,1800,3600]
dirs=[]

pattern=r"([0-9]+)"

infofile = "/home/sgl/projects/global-tsunami-amplification-factors/calculate_AF/location.txt"
factorsfile="factors_all"


outfile=open(factorsfile,'w')

#read file with ID (RIGA) and lon/lat (old numbering)
data={}

fil=infofile
for line in open(fil,'r').readlines()[1:]:
    line=line.strip().split()
    #print("infofile",line)
    #try:
    id=int(line[0])
    id="%04d" %id
    print(id)
    data[id]=[float(line[1]),float(line[2]),False]
    #except:
    #    pass




outfile.write("#global_id lon lat lead 120 200 300 600 1000 1800 3600 lead  120 200 300 600 1000 1800 3600 depth folder\n")


count=0
counterr=0
for d in sorted(os.listdir(simdir)):
    dd=os.path.join(simdir,d)
    m=re.search(pattern,d)
    if m:
        pass
    else:
        continue
    #print("match",pattern,d)
    #for f in sorted(os.listdir(dd)):
    found=False
    #print f
    # m=re.search(pattern,f)
    # if m:
    #     idn=int(m.group(1))
    #     #print "profile",idn
    #     idn="%02d" %(idn)
    # else:
    #     continue
    idntot=str(d)
            
    #skip point if not in data
    if idntot not in data:
        #print("not in data",idntot)
        continue
    
    #print "dir2:",f
    #ampfact for neg/pos, periodes (120-3600)
    out={}
    out["id"]=int(idntot)
    out["neg"]={}
    out["pos"]={}

    #save to file
    lon=data[idntot][0]
    lat=data[idntot][1]
    cmd="%(idntot)s %(lon)3.6f %(lat)3.6f" %vars()
    missing=cmd


    try:
        countpt=0
        for lead in ["neg","pos"]:
            fil="prof%(idntot)s_%(lead)s_factor" %vars()
            for line in open(os.path.join(simdir,d,fil),'r').readlines():
                count+=1
                line=line.strip().split()
                out[lead][int(line[0])]=line[1]
                ampf_depth=float(line[2])
                if float(line[1])> 800000000000: # and float(line[0])>3000:
                    print("error?",idntot,line[1],line[0],lead)
                    countpt=1
                    
            cmd+=" "+lead
            for p in periodes:
                cmd+=" "+str(out[lead][p])
        #print cmd
        if not countpt:
            outfile.write(cmd+" "+str(round(ampf_depth,1))+" "+os.path.join(dd,idntot)+"\n")
            found=True
        if countpt:
            counterr+=1
    except:
        pass
    data[idntot][2]=found

    #if count==100:
    #    break
outfile.close()

print(f"Counted errors: {counterr} errors out of {count} AF simulations")

#errorlog: wich hazardpoints is without amp.fact.
outmissing=open("missing" ,'w')
for i in sorted(data.keys()):
    if not data[i][2]:
        lon=data[i][0]
        lat=data[i][1]
        cmd="%(i)s %(lon)3.6f %(lat)3.6f\n" %vars()
        outmissing.write(cmd)
outmissing.close()
