#!/usr/bin/python3



#import netCDF4
import numpy as np
import matplotlib, os
#matplotlib.use('Agg') # Use non-interactive backend to be able to run outside main thread
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.signal import find_peaks





def waveform(time,eta,out,plot_dir,treshold=0.05,plot=False,quiet=True, tsample=30):
    if not os.path.isdir(plot_dir) and plot:
        os.mkdir(plot_dir)
    period,hmax=-1.0,-1.0
    t=time
    polarity="neg"
    ts_sampl=t[1]-t[0]  #sampling of time-series in seconds
    #convert to about 30 sec sampling:
    corr_sampl=int(np.ceil(tsample/ts_sampl))
    if corr_sampl>1:
        t=t[::corr_sampl]
        eta=eta[::corr_sampl]
        ts_sampl=t[1]-t[0]  #sampling of time-series in seconds
    Nt=len(t)

    ts=eta
    

    #theshold for considering the time-series
    #tsh=0.05
    tsh=treshold

    hmax_all=np.max(ts)
    hmin_all=np.min(ts)
    ihmax_all=np.argwhere(ts==hmax_all)
    ihmin_all=np.argwhere(ts==hmin_all)
    ts_pos=np.argwhere(ts>tsh)
    ts_neg=np.argwhere(ts<-tsh)

    if (hmax_all!=hmin_all and len(ts_pos)!=0 and len(ts_neg)!=0):
        #Automatic picking by Variance
        padding_L=500
        padding=np.zeros(padding_L);
        ts_tmp=np.hstack((padding,ts))
        vts=np.zeros(len(ts_tmp));
        
        for j in range(1,len(ts_tmp)):
            vts[j]=np.var(ts_tmp[0:j])

        
        t0=np.argwhere(vts>0)
        t0=t0[0][0]-padding_L

        #Variance along the time-series
        v=np.zeros(Nt)

        for j in range(1,Nt):
            v[j]=np.var(ts[0:j])

        
        r_sm=20
        var_sm=lowess(exog=t[0::r_sm],endog=v[0::r_sm],frac=0.5)
        peaks,_=find_peaks(var_sm[:,1])

        #if len(peaks)>1:
            #print("is this possible, more than one max???")
            #sys.exit()
        
        if len(peaks)==0:
            if not quiet:
                print("no peaks in variance ...")
            L=Nt*ts_sampl/60
            tshL=int(L*60/ts_sampl)

        else:
            if not quiet:
                print("one or more peaks in variance, picking the first")
            peak=peaks[0]*r_sm
            L=peak*ts_sampl/60
            tshL=int(L*60/ts_sampl)  

        Lwin=120    #window length in minutes for filtering
        ptLwin=int(Lwin*60/ts_sampl) #window in terms of samples

        Ltsh=90     #minimum lengt of the time-series to be accepted (minutes)
        ptLtsh=int(Ltsh*60/ts_sampl)

        if [(t0+tshL)<=Nt]:
            hmax=np.max(ts[t0:(t0+tshL)])
        else:
            hmax=np.max(ts[t0:Nt])

        if [((Nt-t0)>ptLtsh) and (hmax>tsh)]:
            #if window is long enough and max h is above treshold
            ihmax=int(np.argwhere(ts==hmax)[0][0])

            # create a smooth curve segment (lowess) with max as midpoint 
            # used for calculation of wave periode measured as time 
            # between two troughs on both sides of max

            wstart=ihmax-int(ptLwin/2)
            wend=ihmax+int(ptLwin/2)

            if ihmax < int(ptLwin/2):
                wstart=0
            elif (Nt-ihmax)<int(ptLwin/2):
                wend=Nt

            #window for smooth curve
            t_win=t[wstart:wend]
            ts_win=ts[wstart:wend]

            r_sm=1
            #y=lowess(exog=t_win[0::r_sm],endog=ts_win[0::r_sm],frac=0.15)
            y=lowess(exog=t_win[0::r_sm],endog=ts_win[0::r_sm],frac=0.3,it=0)
            corr_filt=np.corrcoef(ts_win[0::r_sm],y[:,1])

            if plot:
                plt.plot(y[:,0]/3600,y[:,1],label="sm")
            
            # make a second smoothing if too different curve from signal
            if corr_filt[1,0]<0.95:
                y=lowess(exog=t_win[0::r_sm],endog=ts_win[0::r_sm],frac=0.11,it=0)  
                #y=lowess(exog=t_win[0::r_sm],endog=ts_win[0::r_sm],frac=0.15,it=0)  
                #y=lowess(exog=t_win[0::r_sm],endog=ts_win[0::r_sm],frac=0.08,it=0)  
                corr_filt=np.corrcoef(ts_win[0::r_sm],y[:,1])
                plt.plot(y[:,0]/3600,y[:,1],label="sm2")


            #find relative maxima and minima of the filtered waveform
            pospeaks,_=find_peaks(y[:,1])
            negpeaks,_=find_peaks(-y[:,1])
            #remove too small peaks and troughs:
            pospeaks=pospeaks[np.argwhere(np.abs(y[pospeaks,1])>0.1*ts[ihmax])][:,0]
            #negpeaks=negpeaks[np.argwhere(np.abs(y[negpeaks,1])>0.1*ts[ihmax])][:,0]
            #find relative minima closest to hmax
            #T1: min to the left of hmax,TS: min to th right of hmax
            
            diff_Tmin_THmax=(y[negpeaks,0]-t[ihmax])
            #if plot:
            #    print("diff_Tmin_THmax",diff_Tmin_THmax/3600,y[negpeaks,0]/3600,y[pospeaks,0]/3600)
            #    print("diff_Tmin_THmax2",y[negpeaks,1],y[pospeaks,1])
            if len(diff_Tmin_THmax)>0:
                idiffneg=np.argwhere(diff_Tmin_THmax<0)
                idiffpos=np.argwhere(diff_Tmin_THmax>0)
 
                if len(idiffneg)==0:
                    #no troughs below zero ahead of max
                    iT2=y[negpeaks[idiffpos[0]],0]
                    yiT2=y[negpeaks[idiffpos[0]],1]
                    iT1=t[ihmax]-(iT2-t[ihmax])
                    yiT1=yiT2
                elif len(idiffpos)==0:
                    #no peaks above zero ahead of max
                    iT1=y[negpeaks[idiffneg[-1]],0]
                    yiT1=y[negpeaks[idiffneg[-1]],1]
                    iT2=t[ihmax]+(t[ihmax]-iT1)
                    yiT2=yiT1
                    
                else:
                    iT1=y[negpeaks[idiffneg[-1]],0]
                    yiT1=y[negpeaks[idiffneg[-1]],1]
                    iT2=y[negpeaks[idiffpos[0]],0]
                    yiT2=y[negpeaks[idiffpos[0]],1]
                    
                
                period=iT2[0]-iT1[0]
                tihmax=t[ihmax]
                #maximum natural waveperiode is 2hrs
                #if problem with neg.trough on both side of tihmax

                # if iT2 > tihmax and np.abs(iT2-tihmax) < 3600:
                #     period_p=iT2-tihmax
                # else:
                #     period_p=False
                #     #for plotting:
                #     iT2[0]=tihmax

                # if iT1 < tihmax and np.abs(iT1-tihmax) < 3600:
                #     period_m=tihmax-iT1
                # else:
                #     period_m=False
                #     #for plotting:
                #     iT1[0]=tihmax

                # #using time between neighboring troughs and tihmax if one side is lacking
                # if period_m and not period_p:
                #     period=2*period_m
                # elif period_p and not period_m:
                #     period=2*period_p
                # elif period_p and period_m:
                #     period=period_p + period_m

                #if plot:
                #    print("period",period,iT2/3600,iT1/3600)
                #    print("tpeak,valpeak",t[ihmax]/3600,ts[ihmax])

                # polarity #################################################
                #find the number of peaks ahead of t[ihmax]
                no_pos_peaks=len(np.argwhere(y[pospeaks,0]<t[ihmax]-0.5*period))
                # negpeaks,_=find_peaks(-ts)
                # #print("negpeaks",negpeaks)

                # diff_Tpol_THmax=negpeaks*2-ihmax
                # idiff_Tpol_neg=np.argwhere(diff_Tpol_THmax<0)
                # idiff_Tpol_pos=np.argwhere(diff_Tpol_THmax>0)

                # #print("tssss",ts[idiff_Tpol_pos[0]])
                # if (ts[idiff_Tpol_pos[0]]>0):
                #     neg_peak_pol_best=0
                #     #print("neg_peak")
                # else:
                #     neg_peak_pol_best=ts[idiff_Tpol_pos[0]]
                #     loc_neg_peak_pol_best=idiff_Tpol_pos[0]
                
                # eval_polar=(np.abs(neg_peak_pol_best)/hmax)*100
                # #print("eval_polar",eval_polar)
                # pol="pos"
                # if eval_polar>25:
                #     pol="neg"


                # if negative, the ratio between the nearest negative trough ahead of highest peak and the highest 
                # peak is larger than a given threshold, let say 0.2
                polratio=np.abs(yiT1)/hmax
                
                polarity="pos"
                if polratio>0.2 and yiT1<0 and no_pos_peaks==0:
                    polarity="neg"
                elif polratio<0.2 and no_pos_peaks==0:
                    polarity="pos"
                elif no_pos_peaks>0:
                    polarity="neg"                       


                if plot:
                    
    
                    plt.stem([iT1/3600,iT2/3600],[yiT1,yiT2])
                    plt.stem([t[ihmax]/3600],[hmax],linefmt='ko--',markerfmt='ko')
                    plt.stem([iT1/3600],[yiT1],linefmt='ko--',markerfmt='ko')
                    plt.plot(t/3600,ts,label="mariogram")
                    plt.xlim([max(t[0]/3600,(t[ihmax]-5400)/3600),min(t[-1]/3600,(t[ihmax]+5400)/3600)])                    
                    cmd="Periode:"+str(int(period))+"s "
                    cmd+=f" hmax: {hmax:.2f} m "
                    cmd+=f" polarity: {polarity}" 
                    plt.title(cmd)
                    plt.legend()
                    plt.xlabel("Time [hrs]")
                    plt.ylabel("Surface elevation [m]")
                    txt=f"{plot_dir}/{out}_eta.png"
                    plt.savefig(txt)
                    print(f"\nInspect plot: {txt}")
                    plt.clf()
            else:
                if not quiet:
                    print("Signal too short")
                if plot:
                    plt.plot(t,ts)
                    cmd=str(id)+" "+str(i)+" Signal too short"
                    plt.title(cmd)
                    plt.legend()
                    plt.savefig(f"{plot}/{out}_short.png")
                    plt.clf()
        else:
            if not quiet:
                print("Threshold not satisfied")
            if plot:
                plt.plot(t,ts)
                cmd=str(id)+" "+str(i)+" Threshold not satisfied"
                plt.title(cmd)
                plt.legend()
                #plt.show()
                plt.savefig(str(plot_dir)+"/test_trs.png")
                plt.clf()
    else:
        if not quiet:
            print("No data")
        if plot:
            plt.plot(t,ts)
            cmd=" Nodata or hmax<tsh"+str(tsh)
            plt.title(cmd)
            plt.legend()
            #plt.show()
            plt.savefig(f"{plot_dir}/{out}.png")
            plt.clf()

    return period, hmax, polarity