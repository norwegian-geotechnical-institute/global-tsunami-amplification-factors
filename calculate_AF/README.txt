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

HOW TO RUN THE MODEL TO CREATE YOUR OWN (CUSTOM) AMPLIFICATION FACTORS

To compute amplification factors for a specific Point of Interest (POI) — typically a wave gauge located at a particular isobath — you can generate a depth profile extending from the shoreline to the deep sea through/or close to the POI. Amplification factors are then calculated based on various wave characteristics, as outlined below.

1. RUNNING EXISTING TEST CASES
    a) Install the required Python packages using the requirements.txt file located in the top-level directory.
    b) Navigate to the calculate_AF folder.
    c) Check the file paths in master.py and post.py to match the location of the example data and script folders.
    d) Here we use the available test profiles in the profiles folder: prof_id0000, prof_id0001, and prof_id0002.
    e) Run the following command to generate amplification factors for all three profiles: python master.py 0 2
        This will create a folder named sim, containing simulation data and amplification factors for each profile.
    f) Run post.py to compile a table of amplification factors for different wave polarities (positive and negative leading waves) and wave periods. 
        The script uses the location.txt file, which includes the coordinates of the POIs. The final output will be saved in a file named factors_all.
- VISUAL INSPECTION OF SIMULATIONS FOR A SPECIFIC PROFILE OR POI
- Use plot.py to generate plots for a specific profile and wave period.
- For example, run:
python plot.py 0000 sim plot 300
This will create plots in the plot folder based on simulations in the sim folder for profile 0000 and a wave period of 300 seconds.
- CREATING YOUR OWN AMPLIFICATION FACTORS
- Extract depth profiles from your own data. Each profile must be a two-column file:
- Column 1: Distance from the shoreline in kilometers
- Column 2: Topography in meters (use negative values for underwater terrain)
- Name each profile file with a numerical suffix, similar to the example profiles.
- Update the paths and naming patterns in master.py and post.py to match your custom profiles.
- Create a location.txt file containing the coordinates of your POIs.
- Run master.py on all profiles to generate simulations.
- Use post.py to compile the results into a factors_all file
