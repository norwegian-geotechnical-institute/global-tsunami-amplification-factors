HOW TO RUN MODEL FOR CREATING YOUR OWN AMPLIFICATION FACTORS

To compute amplification factors for a given point of interes (POI - typically a wave gague at a given isobath) you can create a depth profile from shoreline to the deep sea through the POI, and calculate the ampfactors for different wave characteristics as described below.

1. Running existing testcases
    - install needed packages (use requirements.txt in top folder)
    - go to folder calculate_AF
    - change paths in master.py and post.py to match your location of the folder(s) to data and scripts
    - available profiles for the testcases in folder "profiles" is prof_id0000, prof_id0001, and prof_id0002
    - run master.py 0 2 (creating factors for all three profiles, starting with 0000 and stopping including 0002), creating folder "sim" populated with simulation data and amplification factors for each profile
    - run post.py to create a table with collected factors for different polarity (negative and positive leading wave) and periodes for all profiles found in floder "sim". post.py uses the file location.txt with coordinates of the POIs. The factors are saved in file "factors_all"

2. Visual check of the simulations for a specific profile/POI   
    - run plot.py (e.g. "python plot.py 0000 sim plot 300" will create plots in folder "plot" of simulations in folder "sim" for profile 0000 and wave periods of 300 s)

3. Creating your own factors.
    - extract depth profiles from your data. Your profiles must be two column files with distance from shoreline in kiometers as first column and the topography in meters as second (negative values in sea)
    - give the profiles a name ending with a counting number as examples above
    - modify paths, pattern of profile names etc. in master.py and post.py
    - create a location.txt files with the coordinates of your POIs
    - run master.py on all profiles
    - create factors_all with post.py

