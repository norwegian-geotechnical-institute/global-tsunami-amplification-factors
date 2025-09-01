#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import re,os
import sys

def find_tpt(i,simfolder):
    #the tppoints are located at same position independent of periode and polarity
    with open(f'{simfolder}/{i:04d}/prof{i:04d}_pos_T3600/sim_log', 'r') as file:
        content = file.read()

    # Match the pattern inside the brackets
    match = re.search(r"tplist\s*\[(.*?)\]", content)
    if match:
        raw_values = match.group(1)
        # Split and clean the values
        values = [float(val.strip().strip("'")) for val in raw_values.split(',')]
        print("Extracted values:", values)


    return values

def plot(i,simfolder,plotfolder,periode):
    
    #extract location of gauges
    [x1_deep,x1_shore]=find_tpt(i,simfolder)
    if not os.path.isdir(plotfolder):
        os.mkdir(plotfolder)
        

    for pol in ['neg','pos']:   
        print(pol)
        plt.figure(figsize=(6,11))    
        plt.subplot(3,1,1)
        arr1=np.loadtxt(f"{simfolder}/{i:04d}/prof{i:04d}_{pol}_factor") 
        plt.title(f"Profile {i:04d}, polarity: {pol}")
        plt.plot(arr1[:,0],arr1[:,1],label=f"{i:04d}")
        plt.xlabel("Wave periode [s]")
        plt.ylabel("Amp.factor")
        plt.legend()


        plt.subplot(3,1,2)
        arr1=np.loadtxt(f"{simfolder}/{i:04d}/prof{i:04d}_{pol}_T120/sim_depth")
        x1,y1=arr1[:,0],-arr1[:,1]*1000
        xcorr=x1[-1]
        x1-=xcorr
        x1=abs(x1)
        plt.plot(x1,y1,label=f"{i:04d}")
        ylim=plt.ylim()
        xlim=plt.xlim()
        xcorrtp=abs(x1_deep-x1_shore)
        plt.plot([xcorrtp,xcorrtp],[ylim[1],ylim[0]],'--r',)
        plt.plot([0,0],[ylim[1],ylim[0]],'--g',)
        
        #print(abs(x2_deep-xcorr))
        plt.xlabel("Distance along profile [km]")
        plt.ylabel("Depth [m]")
        plt.legend()
 
        plt.subplot(3,1,3)
        per=periode
        plt.title(f"Periode {per} s")
        tscale=10.1
        arr1=np.loadtxt(f"{simfolder}/{i:04d}/prof{i:04d}_{pol}_T{per}/sim_e_tpt1")
        arr2=np.loadtxt(f"{simfolder}/{i:04d}/prof{i:04d}_{pol}_T{per}/sim_e_tpt2")
        plt.plot(tscale*arr1[:,0],1000*arr1[:,1],'r',label=f"{i:04d}-offshore")
        plt.plot(tscale*arr2[:,0],1000*arr2[:,1],'g',label=f"{i:04d}-shorel")

        plt.xlabel("Time [s]")
        plt.ylabel("Surf.elev [m]")
        plt.legend()
    
        plt.tight_layout()

        #plt.show()
        txt=f"{plotfolder}/plot_prof{i:04d}_{pol}"
        print(f"Figure saved in {txt}")
        plt.savefig(txt)
        plt.clf()


if __name__=="__main__":
    periodes=[120,300,600,1000,1800,3600]
    try: 
        id=int(sys.argv[1])
        simfolder=str(sys.argv[2])
        plotfolder=str(sys.argv[3])
        periode=int(sys.argv[4])
        if periode not in periodes:
            print(f"Your chosen wave periode ({periode}) is not in {periodes}")
            sys.exit()
    except:
        print("Usage: python plot_id.py <id (4 digits)> <nane of simulation folder> <name of folder for plot> <wave period>")
        sys.exit()

    plot(id,simfolder,plotfolder,periode)