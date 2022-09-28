#!/bin/sh

#previous delivery:

touch tmp

for d in ../toJ*/res*
do

echo $d
cat $d >> tmp

done

mawk '{print $2,$3,$5}' tmp > prev
removefirstline.py prev

gmt_plot.py -w -K prev/0.05+ -R-30/330/-60/74 -J M -z 1/7/1 -x a60f30 -p prev.ps




#new ampfactors:

cp ~/projects/GAR2013/domains/Australia/cont/gauges ampf_Aus
mawk '{print $2,$3,$5}' ampf_Aus > new 

cp ~/projects/GAR2013/domains/AmSE/cont/gauges  ampf_AmSE
mawk '{print $2,$3,$5}' ampf_AmSE >> new 

cp ~/projects/GAR2013/domains/AfrS/cont/gauges  ampf_AfrS
mawk '{print $2,$3,$5}' ampf_AfrS >> new 

cp ~/projects/GAR2013/domains/NZL/cont/factors/cont/gauges ampf_NZL
mawk '{print $2,$3,$5}' ampf_NZL >> new 

cp ~/projects/GAR2013/domains/Kamtsj/cont/factors/cont/gauges ampf_Kamch
mawk '{print $2,$3,$5}' ampf_Kamch >> new 

gmt_plot.py -w -K new/0.05+ -R-30/330/-60/74 -J M -z 1/7/1 -x a60f30 -p new.ps



cat prev new > all
gmt_plot.py -w -K all/0.05+ -R-30/330/-60/74 -J M -z 1/7/1 -x a60f30 -p all.ps
