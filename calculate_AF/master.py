#!/usr/bin/python

import os, re, bibl, time, json, sys

try: 
    idstart=int(sys.argv[1])
    try:
        idslutt=int(sys.argv[2])
    except:
        #only one profile
        idslutt=idstart
    print("idstart,idslutt",idstart,idslutt)
except:
    print("You must specify the POI_ID start and stop")
    sys.exit()


mainfolder="/home/sgl/projects/global-tsunami-amplification-factors/calculate_AF"
#put your profiels here:
profiles_folder=os.path.join(mainfolder,"profiles")
#name pattern of filenames (profiles)
pattern=r"prof_id([0-9]+)"  #pattern of file with depth profile
profname_stem="prof_id"
#format of numbering
id_pattern="{:04d}"
#must be unchanged:
periodes=[120,200,300,600,1000,1800,3600] 
#simulation results are put here:
outfolder=os.path.join(mainfolder,"sim")
eps=0.5  #min height in meters of wave to be counted for (initial height is 1 m, so eps<1.0)

ampf_depth=99    #depth in meters at offshore gauge 
#ampf_depth="end"  #use this flag if you will use the outermost point of profile (deep end) 
#ampf_depth="ext_end" #outermost point of profile included added extention with constant depth

#shape of forced input (scaled):
unitpulse=os.path.join(mainfolder,"unitpulse")

#do no simulations only postprocessing
#nosim=True
nosim=False

start=os.getcwd()
if not os.path.isdir(outfolder):
    os.mkdir(outfolder)
os.chdir(outfolder)

problem=[]
timeall=time.time()
count=0
os.chdir(outfolder)

if not os.path.isdir(profiles_folder):
    print("The folder with profiles,",profiles_folder,", does not exist ....")
    sys.exit()
os.chdir(profiles_folder)

#divide into several groups for parallell run
cc=0
nn=len(os.listdir(os.curdir))
# change eps into km:
eps*=0.001
if ampf_depth not in  ['end','ext_end']:
    ampf_depth*=0.001

for id in range(int(idstart),int(idslutt)+1): 
    #run through all profiles (idnumber=htp)
    id=id_pattern.format(id)
    prof=os.path.join(profiles_folder, profname_stem+str(id))
    
    CPUhpt=time.time()
    



    if not os.path.isfile(prof):
        cmd=f"{id}: Profile doesn't exist - continuing to next profile"
        print(cmd)
        problem.append(cmd)
        continue
    
    ####################################################
    #
    # running wave model
    #
    ####################################################
    
    try:
        problem,count=bibl.run(id,ampf_depth,periodes,id,prof,outfolder,count,problem,nosim,eps,unitpulse)  
    except:
        cmd="id "+str(id)+": Problem with running the model (problem with profile?)"
        problem.append(cmd)
        print("count - after",count)

    CPUhpt=time.time()-CPUhpt
    file=open("CPU-%.2fs" %(CPUhpt),'w')
    file.close()

    #displaying progress if running a large number of profiles
    nn=int(idslutt)-int(idstart)+1
    cc+=1
    part=float(100)/nn*cc
    print("%"*60)
    pr="%"
    sec=time.time()-timeall
    cmd="After %(sec).0f sec: simulating %(cc)d out of %(nn)d (%(part).2f %(pr)s) profile: %(id)s\n" %vars()
    print(cmd)
    print("Simulating ",cc,"out of",nn,"(",str(part)," %)")
    print("%"*60)

timeall=time.time()-timeall
print("Totally",count,"simulations")
print("Total time",timeall)
print("Problem",problem)
#json.dump(problem, open("problem",'w'))
os.chdir(outfolder)
fil=open("problem",'w')
for line in problem:
    fil.write("%s\n" %(line))
fil.close()

   
