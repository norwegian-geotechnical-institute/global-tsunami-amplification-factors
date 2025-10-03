HOW TO CALCULATE MIH FROM TIME SERIES AND TABLES WITH AMPLIFICATION FACTORS

Surface elevation time series are extracted at designated offshore Points of Interest (POIs).

1. Calculating MIH from a single time series / POI
    Each time series in an ascii txt file should contain two columns: time [sec] and surface elevation [m].
    a) Use the script calculate_MIH_general.py. Change paths etc. in the main section to match the location of the files in your system. An example dataset and usage are provided in the main section at the end of the file.
    b) Run the script using: python calculate_MIH_general.py
    c) Results will be printed to the screen.
    d) To process multiple POIs, modify the script to loop through several time series, redirect output to a file, and apply custom amplification factors (see the calculate_AF folder).

2. HySEA: Calculating MIH from multiple time series / POIs using existing example 
    a) Compile the code in the postprocess_HySEA folder. Refer to README.txt and the shell script for compilation instructions. You may also try the precompiled version.
    b) Extract waveforms from HySEA output:
        - Navigate to the example folder
        - Run: ../../postprocess_HySEA/postprocess_HySea result_ts.nc
        - This will generate result_ts.nc.offshore.txt with waveforms and offshore heights.
        - Return to the root folder: cd ..
    c) Run calculate_MIH_HySEA.py to compute MIH for all POIs.
        - Modify paths in main-section to match the location of files in your system.
        - Output will be saved to example_HySEA/calculated_MIH_HySEA.txt
        - Required: example_HySEA/result_ts.nc_id.txt, which maps POI IDs to amplification factors and locations. The first line must indicate the number of time series in the HySEA run.

3. Running HySEA from scratch with precomputed global amplification factors
    a) Extract an ID file for time series locations from the precomputed amplification factor dataset. This file should include POI ID, longitude, and latitude, with the first line indicating the number of time series locations. See the example folder for format.
    b) Modify the file from step (a) to serve as HySEA input, maintaining the same POI order.
    c) Run HySEA using the modified input file.
    d) Post-process the NetCDF output using postprocessHySEA.
    e) Adjust calculate_MIH_HySEA.py to match the files from step (a).

4. Running HySEA with custom amplification factors
    a) Follow instructions in the ../calculate_AF folder. Bathymetric profiles for each POI are required. All computed factors are saved in a file.
    b) Repeat steps (a)–(e) from section 3 above.
