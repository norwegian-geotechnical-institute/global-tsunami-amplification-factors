HOW TO CALCULATED MIH FROM TIMESERIES AND TABLE WITH AMPLIFICATION FACTORS

Time series are extracted as surface elevations at given offshore point of interest (POIs)

1. Calculate the MIH from a single timeserie/POI of surface elevation (columns time [sec] and surface elevation [m]).
    a) use calculate_MIH_general.py. Example is given in main-section in the end of file, with example dataset
    b) run python calculate_MIH_general.py
    c) results are printed to screen
    d) modify script to run over several points, redirecting output data to file, apply own ampfactors (see calculate_AF folder) etc.

2. Calculate the MIH from several timeseries/POIs using HySEA - using example files 
    a) Compiling code in postprocess_HySEA folder. Se README.txt and shellscript with compiling instructions
    b) Extract waveforms from HySEA output: 
        cd example_HySEA
        ../../postprocess_HySEA/postprocess_HySea result_ts.nc  #will produce file result_ts.nc.offshore.txt with waveforms and offshore heights
        cd ..
    c) Running calculate_MIH_HySEA.py will create outputfile with MIH for all timeseries/POIs in HySEA output here: example_HySEA/calculated_MIH_HySEA.txt
        - see main-section of script to how to modify for your own HySEA simulations, your own factors etc.
        - a file like example_HySEA/result_ts.nc_id.txt is needed. This reflects the id in ampfactor file and the location of the POIs in the HySEA simulations. The first line contain the number of timeseries in the HySEA run. 

3. Running HySEA from scratch using precomuted global ampfactors
    a) extract an id file for loctation of timeseries extraction as a subset of global_id with POIs within your computational domain including lon, and lat, with the number of the number of timeseries location as the first digit (see example folder for format)
    b) modify file from a) that should be the input of timeseries location for HySEA but with the same sequence of the lon/lat as in a)
    c) run HySEA with file from b)
    d) run postprocessHySEA on netcdf-output
    e) modify calculate_MIH_HySEA.py to match files from a) and 

4. Running HySEA from scratch with own ampfactors
    a) follow description from folder ../calculate_AF. Bathymetric profiles for each POI is neeeded. All factors saved in a file
    b) follow a)-e) under pt. 3 above. 