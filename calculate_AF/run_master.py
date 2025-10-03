#!/usr/bin/python

from GloBouss import GloBouss 
import os,shutil,multiprocessing


def run(start,stop):
    os.system(f"python master.py {start} {stop}")


#divide 
param=[]
# param.append((1,3000))
# param.append((3001,6000))
# param.append((6001,9000))
# param.append((9001,12000))
# param.append((12001,15000))
# param.append((15001,18000))
# param.append((18001,21000))
# param.append((21001,23000))

param.append((1,500))
param.append((501,1000))
param.append((1001,1500))
param.append((1501,2000))
param.append((2001,2500))
param.append((2501,3000))
param.append((3001,3500))
param.append((3501,4000))

nproc=7
with multiprocessing.Pool(processes=nproc) as p:
    print(f"Number of CPU's {multiprocessing.cpu_count()}") 
    p.starmap(run,param)