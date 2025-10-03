import netCDF4
import numpy as np
#read in netcdf
file = netCDF4.Dataset("result_ts.nc", 'r')
string=""
for f in file.variables.keys():
    string+=f+" "
print("This is the variables of the NetCDF-file:",string) 

lat   = file.variables["latitude"][:]
lon   = file.variables["longitude"][:]
time  = file.variables["time"][:]
depth = file.variables["deformed_bathy"][:]
eta   = file.variables["eta"][:]
#save every nth tms to a two-column file with a running number

for i in range(0,len(eta[0,:]),500): #[2587,2588,2589]: #[25,31,32]: #r
    print(i)
    data=np.column_stack((time,eta[:,i]))
    tms=f"tms_{i:05d}.txt"
    np.savetxt(tms,data)
