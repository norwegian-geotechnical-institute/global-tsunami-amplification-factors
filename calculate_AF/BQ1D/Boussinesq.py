#!/usr/bin/python

import os, sys, getopt,math
import time as TIME

#from numarray import *
from sct.sio import sio
from sct.Grid1D import Grid1D
import numpy
from sct.Wave1D import Wave1D


class Boussinesq:
    def __init__(self,**kwargs):
        """... init ..."""
        global Bou

        #default values
        kwa={}
        kwa['vario']      = True     #variogrid - const. Courant number
        kwa['dx']         = 0        #if dx>0: uniform grid
        kwa['eps']        = 0        #dispersive terms
        kwa['alpha']      = 0        #non-linear terms
        kwa['tstop']      = 100      #termination time
        kwa['dt']         = 1        #time increment
        kwa['tssave']     = 0        #time between each saving of timeseries
        kwa['tsave']      = 1        #time between each saving of surface/vel.
                                     #for t=0 and t=tstop is saved
        kwa['safety']     = 1        #safetyfactor
        kwa['nump']       = False    #using python for solving (not C)
        kwa['plotu']      = False    #plot velocity fields and timeseries?
        kwa['ploteta']    = True     #plot velocity fields and timeseries?
        kwa['plotetaH']   = False    #plot ratio eta to depth
        kwa['cdepth']     = 1        #value of constant dept
        kwa['radiation']  = False
        #boundary:
        kwa['boundary']   = False    #feeding the simulator with eta
                                     #on x=xs if  boundary="filename"
        kwa['bysc']       = 1        #yscaling of boundary feeded ic/nested
        kwa['btsc']       = 1        #time scaling of boundary/nested sol.
        kwa['boundary_u']   = False
        kwa['Bysc']       = 1        #yscaling of boundary feeded ic/nested
        kwa['Btsc']       = 1        #time scaling of boundary/nested sol.
               
        #slide:
        kwa['slidet']     = False    #if timedependent depth give filename:
                                     #2 columns: t and pos of center of slide
                                     #NB scaled values!!!
        kwa['slide']      = False    #shape of slide (positiv values) to be
                                     #to be added to the depth
        kwa['sladd']      = 0        #adding this value to the position of
                                     #slide: (t,pos) is now (t,pos+add)
        kwa['etainstab']  = 10000    #terminating if eta becomes larger
                                     
        #slide configuration ala skredp:
        kwa['Ra']         = 0        #acelleration distance
        kwa['Rc']         = 0        #distance of constant velocity
        kwa['Rd']         = 0        #decelleration distance
        kwa['L']          = 0        #length of slide
        kwa['dH']         = 0        #height of slide
        kwa['S']          = 0        #smooth length (def: S=L/2)
        kwa['vmax']       = 0        #maximum velocity (scaled!!), if vmax=1
                                     #the time-position of slide must be
                                     #given by 'slidet'
        
        kwa['skpslide']   = False    #indicator for this slide configuration

        
        kwa['kappa']      = 0        #parameter for improved disp. (-0.531)
                                     #if kappa=0 - without improved terms
        #makegrid1D:
        kwa['casename'] = "out"
        kwa['casedir']  = None
        kwa['tplist']  = []
        kwa['H']       = 0.001    #crit detph for smallest dx
        kwa['C']       = 1        #Courant number only for variogrid
        kwa['xs']      = None     #start of domain
        kwa['xe']      = None     #end of domain
        kwa['quiet']   = 0        #reduces output to screen



        #update globals/self.prm:
        self.prm=kwa
        self.prm.update(kwargs)
        globals().update(self.prm)

        #make directory for storing files:
        try:
            if not os.path.isdir(casedir):
                os.mkdir(casedir)
        except:
            pass

        #write out kwargs:
        string="("
        for i in kwa.keys():
            if str(type(kwa[i]))[7:-2]=="str":
                string+=str(i)+"=\""+str(kwa[i])+"\","
            else:
                string+=str(i)+"="+str(kwa[i])+","
        string=string[:-1]+")"
        if casedir:
            fname=os.path.join(casedir,".kwargs")
        else:
            fname=".kwargs"
        file=open(fname,'w')
        file.write(string)
        file.close()


        #checking of parameters:
        
        #saveing of fields:
        if self.prm['tsave']<=0:
            self.prm['tsave']=self.prm['tstop']
            
        #saveing of timeseries:
        if self.prm['tssave']<self.prm['dt']:
            self.prm['tssave']=self.prm['dt']

        #variogrid
        if self.prm['dx']>0:
            self.prm['vario']=False

        #input on boundary:
        #--------------------------------------------------
        if self.prm['boundary']:
            d=sio(quiet=self.prm['quiet'])
            [self.prm['t0'],self.prm['eta0']]=d.read(self.prm['boundary'])
            self.prm['t0']*=self.prm['btsc']
            self.prm['eta0']*=self.prm['bysc']
            if self.prm['boundary_u']:
                [self.prm['tu0'],self.prm['u0']]=d.read(self.prm['boundary_u'])
                self.prm['tu0']*=self.prm['Btsc']
                self.prm['u0']*=self.prm['Bysc']
            

        #submarine slide:
        #--------------------------------------------------
        if Ra or Rc or Rd:
            if L==0 or dH==0:
                print("""
                You must specify the length (L) and the height (dH)
                of the slide!!""")
                sys.exit()
            else:
                self.prm['skpslide']=True
            if not S:
                self.prm['S']=L/2.0
            globals().update(self.prm)
        d=sio(quiet=self.prm['quiet'])
        if self.prm['slidet'] or self.prm['slide'] or  self.prm['skpslide']:
            if self.prm['slidet'] and self.prm['slide']:
                [self.prm['slt'],self.prm['slcx']]=d.read(self.prm['slidet'])
                [self.prm['slx'],self.prm['sly']]=d.read(self.prm['slide'])
            elif self.prm['skpslide']:
                if vmax:
                    #compute time/position ala skredp:
                    result=self.slide_tpos(Ra,Rc,Rd,vmax,sladd)
                    self.prm['slt'],self.prm['slcx']=result
                else:
                    #time and position to slide read from file:
                    result=d.read(self.prm['slidet'])
                    [self.prm['slt'],self.prm['slcx']]=result
                self.prm['slx'],self.prm['sly']=self.slide_config(L,S,dH)
                self.prm['skpslide'] = True
            else:
                print("You must specify both the time evolution of the")
                print("center of mass (or x=0) of the slide (file specif.")
                print("by 'slidet' or Ra,Rc,Rd,L,dH,S,vmax), and the shape ")
                print("of the slide (file specified by param. 'slide' or ")
                print("the parameters Ra,Rc,Rd,L,dH,S) ")
                sys.exit()

            if casedir:
                fname=os.path.join(casedir,".slidepos")
            else:
                fname=".slidepos"
            d.write(fname,self.prm['slt'],self.prm['slcx'])
            if casedir:
                fname=os.path.join(casedir,".slide")
            else:
                fname=".slide"
            d.write(fname,self.prm['slx'],self.prm['sly'])
            
        #end slide --------------------------------------------------

        globals().update(self.prm)
        

        #kwarg for variogrid:
        self.kwavg={}
        for i in ('H','C','xs','xe','dt'):
            self.kwavg[str(i)]=self.prm[i]

        #solving by using NumPy or wrapped C:
        if nump:
            print("numpy",alpha,eps)
        if alpha == 0 and eps == 0:
            print("Using LSW")
            import BQ1D.LSW as Bou
        elif nump:
            print("Using BoussNumPy")
            import BoussNumPy as Bou
        else:
            try:
                import BoussPyC as Bou
                print("Using BoussPyC")
            except:
                import BoussNumPy as Bou
                print("BoussPyC (wrapped C solver) is not properly \
                       installed/build,using BoussNumPy instead")



    def slide_config(self,L,S,dH):
        """produces a slide ala skredp"""
        print(">>> shape of slide ala skredp <<<")
        length=L+2*S
        n=100   #100 nodes along the slide source
        dx=float(length)/n
        g=Grid1D()
        X=g.uniformgrid(0,length,dx)
        Y=X.copy()
        i=0
        for x in X:
            if x<=S:
                Y[i]=dH*math.exp(-(2*(S-x)/S)**4)
            elif S<x<L+S:
                Y[i]=dH
            elif x<=L+2*S:
                Y[i]=dH*math.exp(-(2*(x-S-L)/S)**4)
            i+=1
        
        X=X-S-0.5*L #x=0 is the rightmost part of the box with y=dH
        return X,Y

    def slide_tpos(self,Ra,Rc,Rd,vmax=1,add=0):
        """produces a time/position procedure ala skredp"""
        print(">>> time/position of slide ala skredp <<<")
        n=500
        Ta=math.pi*Ra/(2*vmax)
        Tc=Rc/vmax
        Td=math.pi*Rd/(2*vmax)
        Tot=Ta+Tc+Td
        dt=Tot/n
        t=numpy.zeros(n)+0.0
        dist=t.copy()

        for i in range(n):
            t[i]=i*dt
            if t[i]<Ta:
                dist[i]=Ra*(1-math.cos((vmax*t[i])/Ra))
            elif Ta<=t[i]<=Ta+Tc:
                dist[i]=Ra+vmax*(t[i]-Ta)
            elif t[i]<Tot:
                dist[i]=Ra+Rc+Rd*math.sin((vmax/Rd)*(t[i]-Ta-Tc))
            elif t[i]>=Tot:
                dist[i]=Ra+Rc+Rd
            else:
                print("something is wrong...")

        return t,dist+add

    def generate_grids(self,depthx=False,depth=False):
        """generate variable and staggered grid using sct.Grid1D.variogrid
        function. depthx and deph is 1D arrays holding the values for the
        depthprofile. Grids are found as 1D arrays in self.gu and self.ge for
        u and eta, respectively, while the corresponding depth is found in
        self.depth (on same grid as u)"""

        global xs,xe
        #uniform grid
        if isinstance(depthx,bool):
            if dx==0:
                print("You must specify the depth or dx")
                sys.exit()
            if str(xs)=='None' or str(xe)=='None':
                print("You must give start (xs) and end (xe) for")
                print("for uniform grid on const. depth")
                sys.exit()

            n=int((float(xe)-float(xs))/dx)+1
            self.gu=numpy.array(range(n),float)*dx+xs
            self.depth=numpy.zeros([len(self.gu)],float)+cdepth
            print("Uniform grid on constant depth =",cdepth)

        #variable grid spacing:
        else:
            #grid with only wet points:
            start=-99999
            end=-99999
            for i in range(0,len(depthx),1):
                if depth[i]>0 and start==-99999:
                    start=i
                    break
            for i in range(len(depthx)-1,0,-1):
                if depth[i]>0:
                    end=i
                    break

             
            depthx=depthx[start:end+1]
            depth=depth[start:end+1]
            #check if there are still negative values for depth in domain:
            test=numpy.less(depth,0)
            if bool(test.any()):
                print("You have negative depth values in domain, check your bathymetry")
                sys.exit(0)
                
            if not xs:
                xs=depthx[0]
            if not xe:
                xe=depthx[-1]

                
            g=Grid1D(depthx,depth)
            #generate grid for u, same as for depth:
            #if dx>0: uniform grid on variable depth:
            if dx>0:
                ####################################
                # denne gir ikke variabel depth -
                # maa interpolere 
                n=int((float(xe)-float(xs))/dx)+1
                self.gu=numpy.array(range(n),float)*dx+xs
                tmp,self.depth=g.interp_lin(self.gu)
                print("Uniform grid on variable depth")
            else:
                x,depth=g.variogrid(x=g.x,y=g.y,**self.kwavg)
                self.depth=depth.copy()
                self.gu=x.copy()
                print("Variable grid on variable depth")

            ############################################################
            ############################################################
            #testing 2016-08-26
            self.depth[-1]=0.000
            #self.depth[-1]=0.0005
            ############################################################
            ############################################################
           
        #generate grid for eta (staggered grid with a node for u at bound.):
        self.ge=(self.gu[:-1]+self.gu[1:])/2


    def checkdomain(self, grid):
        print("check domain")
        if str(xs)!='None' and str(xe)!='None':
            if grid[0]>xe or grid[-1]<xs:
                print("Your input data is outside the computational domain!")
                print("Bailing out ...")
                sys.exit(0)

        
    def init(self,xeta=False,eta=False,xu=False,u=False,
             xdepth=False,depth=False):
        """fill initial condition and depth. xeta/eta and xu/u is surface
        elevation and velocity given on arbitrary grids. If non are given,
        eta=u=0, and depth=cdepth. This function will generate a staggered
        grid (uniform if xdepth=False, spacing given by the value of dx>0)."""

        global savetimefields
        #generate grid
        if not isinstance(xdepth,bool):
            self.checkdomain(xdepth)
        self.generate_grids(xdepth,depth)
        #find increment
        self.incr=self.gu[1:]-self.gu[:-1]
         
        #fill IC:----------------------------------------
        self.u=numpy.zeros([len(self.gu)],float)
        #if xu and u=False: intitial u=0, else interp values from u:
        if not isinstance(xu,bool):
            self.checkdomain(xu)
            g1=Grid1D(xu,u)
            x,self.u=g1.interp_lin(self.gu)
        #interpolate eta on new grid:
        self.eta=self.ge.copy()*0.0
        if not isinstance(xeta,bool):
            self.checkdomain(xeta)
            g2=Grid1D(xeta,eta)
            x,self.eta=g2.interp_lin(self.ge)

        
        #init results/timeseries:
        self.tp=[] #list with all info/data from timeserie points
        self.etashoreline={}
        self.etashoreline['time']=[]
        self.etashoreline['eta']=[]

	#init amplitude leading wave
        self.amp={} #amplitude of leading wave

        for i in range(len(tplist)):
            ## if float(tplist[i])>xe or float(tplist[i])<xs:
            ##     print "\n\nSome of your timeserie points are located outside"
            ##     print "the computational domain ... Bailing out!!!"
            ##     print "This point is outside x="+str(tplist[i])+".\n\n"
            ##     sys.exit(0)
            if float(tplist[i])>xe:
                print("#"*30)
                print("Your timeserie is located outside the domain")
                print("and is moved to closest gridpoint")
                print("Old location",tplist[i])
                print("New location",xe)
                print("#"*30)
                tplist[i]=xe
            if float(tplist[i])<xs:
                print("#"*30)
                print("Your timeserie is located outside the domain")
                print("and is moved to closest gridpoint")
                print( "Old location",tplist[i])
                print("New location",xs)
                print("#"*30)
                tplist[i]=xs
               

            self.tp.append({})
            self.tp[i]['time']=[]
            self.tp[i]['u']=[]   #list with time evolution of velocity
            self.tp[i]['eta']=[]
            self.tp[i]['x']=float(tplist[i]) #position of point
            d=Grid1D(self.gu,self.depth)
            self.tp[i]['depth']=d.interp_lin([float(tplist[i])])[1][0]

        #counter for number of loops in timeloops:
        self.count=1
        #save init results
        self.files={}
        self.files['head'] = "Generated files for eta and u:\ntime \teta \tu"
        self.files['time'] = []
        self.files['eta']  = []
        self.files['u']    = []
        self.files['H']    = []
        self.files['etaH'] = []
        
        savetimefields=0
        self.saveresults(0)


    def saveresults(self,time):
        """saveing eta/u and updating timeseries"""
        global savetimefields
        f=Grid1D()
        #eta shoreline:
        self.etashoreline['time'].append(time)
        self.etashoreline['eta'].append(self.eta[-1])
        #timeseries:
        for i in range(len(tplist)):
            f.update(self.gu,self.u)
            self.tp[i]['u'].append(float(f.interp_lin([self.tp[i]['x']])[1][0]))
            f.update(self.ge,self.eta)
            self.tp[i]['eta'].append(float(f.interp_lin([self.tp[i]['x']])[1][0]))
            self.tp[i]['time'].append(time)
	#find amp of leading wave
        #w=Wave1D(eps=0.001)
        #try:
        #    d=w.front(self.ge,self.eta,dir='right',no=1)
        #    xamp,amp=d[0]['crest'][0],d[0]['crest'][1]
        #    xamp="%.5f" %(xamp)
        #    if amp>0.001:
        #        self.amp[xamp]=str(time)+" "+str(amp)
        #except:
        #    pass
        
        #save eta/u only each
        if  time-savetimefields>=tsave or time==0:
            print("saveing at time",time)
            #save files for eta/u
            etafile="."+casename+"_e"+str(self.count)
            ufile  ="."+casename+"_u"+str(self.count)
            Hfile ="."+casename+"_H"+str(self.count)
            etaHfile ="."+casename+"_etaH"+str(self.count)
            if casedir:
                etafile=os.path.join(casedir,etafile)
                ufile=os.path.join(casedir,ufile)
                Hfile=os.path.join(casedir,Hfile)
                etaHfile=os.path.join(casedir,etaHfile)
            save=sio(quiet=quiet)
            self.files['time'].append(time)
            if ploteta:
                save.write(etafile,self.ge,self.eta)
                #files[] holds the name of the files:
                self.files['eta'].append(etafile)
            if plotu:
                save.write(ufile,self.gu,self.u)            
                self.files['u'].append(ufile)
            if plotetaH:
                r=self.eta/self.depth[:-1]
                save.write(etaHfile,self.ge,self.eta/self.depth[:-1])            
                self.files['etaH'].append(etaHfile)
		
            if (slide or skpslide) and time>0:
                save.write(Hfile,self.gu,-olddepth)            
                self.files['H'].append(Hfile)
            
            savetimefields+=tsave
            self.count+=1

    def write_fileoverview(self):
        """writing a file with overview over generated files for eta/u"""
        if casedir:
            cname=os.path.join(casedir,casename)
        else:
            cname=casename
        file=open(cname+".map",'w')
        if plotu:
            file.write("\ttime \teta \tu\n\n")
            for i in range(len(self.files['eta'])):
                fi=(self.files['time'][i],self.files['eta'][i],self.files['u'][i])
                file.write("%12.4f \t%s \t%s\n" % fi)
        else:
            file.write("\ttime \teta\n\n")
            for i in range(len(self.files['eta'])):
                fi=(self.files['time'][i],self.files['eta'][i])
                file.write("%12.4f \t%s\n" % fi)

        file.close()


    def write_timeseries(self):
        #overview over positions and files
        if casedir:
            cname=os.path.join(casedir,casename)
        else:
            cname=casename
        name=cname+"_tms.map"
        file=open(name,'w')
        if plotu:
            file.write("pt.# \tx-pos \t\tdepth \teta \tu\n\n")
        else:
            file.write("pt.# \tx-pos \t\tdepth \teta\n\n")
        for i in range(len(tplist)):
            no=i+1
            ename=cname+"_e_tpt"+str(no)
            uname=cname+"_u_tpt"+str(no)
            it=self.tp[i]
            if plotu:
                file.write("%4d %12.8f %12.8f \t%s \t%s\n" \
                           %(no,it['x'],it['depth'],ename,uname))

            else:
                file.write("%4d %12.8f %12.8f \t%s\n" \
                           %(no,it['x'],it['depth'],ename))
            #write data to file
            etaf=open(ename,'w')
            uf=open(uname,'w')

            for i in range(len(it['eta'])):
                etaf.write("%f %.12f\n" %(it['time'][i],it['eta'][i]))
                uf.write("%f %.12f\n" %(it['time'][i],it['u'][i]))
            uf.close()
            etaf.close()


        #write shoreline values
        etashore=open(cname+"_shoreline",'w')
        for i in range(len(self.etashoreline['time'])):
            etashore.write("%f %.12f\n" %(self.etashoreline['time'][i],self.etashoreline['eta'][i]))
        etashore.close()

        file.close()
        
        

    def write_results(self):
        if casedir:
            cname=os.path.join(casedir,casename)
        else:
            cname=casename
        self.write_timeseries()
        self.write_fileoverview()
        self.write_logfile(cname)
        #write amplitude-file
        #fil=open(cname+"_amp",'w')
        #for key in self.amp.keys():
        #    fil.write("%f %s\n" %(float(key),self.amp[key]))
        #fil.close()
        print("\nLogfile: ",cname+"_log")
        print("Casename: ",cname)
        print("Generated surface/velocity files, see:",cname+".map")
        print("Generated files for timeseries, see: "+cname+"_tms.map\n\n")


    def solve(self):
        global dt,tlevels,savetimefields,newdepth,olddepth
        time=0
        dt*=safety
        #number of timelevels between saving of fields
        #(runnung a loop in c-code until next saveing)
        tlevels=int(tssave/dt)
        #number of timelevels between saving of timeseries:
        tslevels=1
        savetime=0
        #running time between each saveing of fields:
        savetimefields=0
        newdepth=self.depth.copy()
        olddepth=self.depth.copy()

        #if boundary must be feeded at each timelevel:
        if boundary or slide or skpslide:
            tslevels=tlevels
            tlevels=1
        cpu=TIME.time()
        if slide or skpslide:
            olddepth=self.add_slide(self.depth,0)
        sm=Grid1D()
	    #plot initial condition
        self.saveresults(time)

        while time<tstop:
            time+=tlevels*dt
            self.solve_at_timesteps(time)
            if self.eta.max() > etainstab:
                print("Maximum value of eta is",self.eta.max())
                print("...and is above the instability criterion",etainstab)
                print("TERMINATING at time %s :-(" % time)
                break
            #print "smoothing at time",time
            #sm.update(self.ge,self.eta)
            #sm.smooth(10,type=5)
            #self.eta=sm.y
            #sm.update(self.gu,self.u)
            #sm.smooth(10,type=5)
            #self.u=sm.y

            
            if time-savetime>=tslevels*dt:
                self.saveresults(time)
                savetime=time
        print("\n\nSimulation finnished in %12.5f seconds!" %(TIME.time()-cpu))
        self.write_results()
        
    def add_slide(self,depth,time):
        d=sio(quiet=quiet)
        tmp=depth.copy()
        #[t,pos]=d.read("f_strek55")
        g2=Grid1D(slt,slcx)
        [t,add]=g2.interp_lin([time])
        #[x,y]=d.read("slide")
        g=Grid1D(slx,sly)
        g.interp_lin(self.gu-add[0])
        tmp-=g.y
        return tmp


 
        
            
    def solve_at_timesteps(self,time):
        """solving at a timestep, using C or NumPy"""
        #default values (corresponds to noflux)
        global newdepth,olddepth #for timedep. depth (slide)
        e0=0
        U0=0
        rad=0
        if slide or skpslide:
            newdepth=self.add_slide(self.depth,time)
        if radiation:
            rad=1
        if boundary:
            g=Grid1D(t0,eta0)
            e0=g.interp_lin([time],t0,eta0)[1][0]
            #depth:
            d0=self.depth[2]
            #velocity
            if boundary_u:
                g=Grid1D(tu0,u0)
                U0=g.interp_lin([time],tu0,u0)[1][0]
            else:
                U0=e0/math.sqrt(d0)
        args=(self.eta,self.u,self.incr,newdepth,olddepth,dt\
              ,alpha,eps,tlevels,e0,U0,rad,kappa)
        Bou.solve_timesteps(*args)
        olddepth=newdepth.copy()

            
    def write_logfile(self,case):
        depth=case+"_depth"
        d=sio(quiet=quiet)
        d.write(depth,self.gu,self.depth)
        name=case+"_log"
        old=""
        if os.path.isfile(name):
            old=open(name,'r').read()
        file=open(name,'w')
        file.write("\n\n#----------------------------------------------------\n\n")
        time_date=TIME.asctime(TIME.localtime(TIME.time()))
        file.write("Time: %s \nScript: %s\n" %(time_date,sys.argv[0]))
        try:
            file.write("Host: %s " %(os.environ['HOST']))
        except:
            file.write("Host: unknown\n")
        file.write("\nParameters:\n\n")
        logfile=""
        for i in self.prm:
            logfile+=str(i)+"\t"+str(self.prm[i])+"\n"
        file.write(logfile+"\n"+old)
        file.close()
        


#run the simulator:
if __name__ == '__main__':

    from sct.io import io
    #new instance:
    Bouss   = Boussinesq(tssave=1,dt=0.5,tplist=[],
                         tstop=50,alpha=0,eps=0,casename="c",safety=0.3,
                         quiet=1,plotu=False,boundary=False,nump=False,
                         radiation=True,slidet="fabio_strek_sc",slide="slide")

    f=sio(quiet=1)
    #depth
    [xH,H]     =f.read("bsc.sort")
    #velocity
    #[xu,u]     =f.read("u0")
    #eta
    [xeta,eta] =f.read("test")
    #ini
    #Bouss.init(xeta,eta,xu,u,xH,H)
    Bouss.init(xdepth=xH,depth=H)
    #Bouss.init()
    #timeloop:
    Bouss.solve()




#############################################################################
#                                                                           #
#                                                                           #
# 12/5-2006: Wrappet C og variogrid fungerer ikke (stoy blaaser opp).       #
#            Verifisert kode med solitaerboelge, konstant dyp.              #
#                                                                           #
# 30/5-2006: Feil rettet:                                                   #
#            return arrayene fra kallet til Grid1D.variogrid maatte         #
#            kopieres (copy()) til arrayene som sendes til BouPyC, ikke     #
#            sette self.arr=arr, men self.arr=arr.copy()                    #
#                                                                           #
# 18/10-2006 Lagt inn undersjoisk skred. Form og utlop bestemmes av         #
#            av data paa input filer                                        #
#                                                                           #
# 7/12-2006  forbedret muligheter ved skred. Kan ogsaa gi parametre ala     #
#            ala skredp.                                                    #
#                                                                           #
# juli-2016  I "init" så er det lagt inn justering av tidsseriepunkter      #
#            om disse er utenfor domenet. Nærmeste gridpunkt velges         #
#                                                                           #
#############################################################################

#  legg inn at man kan velge om eta skal skrives ut (kun tidsserier)
#  legg inn at man kan velge save step for baade tidsserie og plot uavhengig
#  legge inn test savetimefields ... i init
#  Implementer veksling mellom tid/posisjon og skredform fra fil og vha parametere, feks tid/posisjon fra fil, og skredform fra parametre.
