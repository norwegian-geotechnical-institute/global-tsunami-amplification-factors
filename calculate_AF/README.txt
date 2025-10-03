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

2. VISUAL INSPECTION OF SIMULATIONS FOR A SPECIFIC PROFILE OR POI

    a) Use plot.py to generate plots for a specific profile and wave period. 
    b) For example, run: "python plot.py 0000 sim plot 300" This will create plots in the plot folder based on simulations in the sim folder for profile 0000 and a wave period of 300 seconds.

3. CREATING YOUR OWN AMPLIFICATION FACTORS

    a) Extract depth profiles from your own data. Each profile must be a two-column file: column 1: Distance from the shoreline in kilometers, column 2: Topography in meters (use negative values for underwater terrain)
    b) Name each profile file with a numerical suffix, similar to the example profiles.
    c) Update the paths and naming patterns in master.py and post.py to match your custom profiles.
    d) Create a location.txt file containing the coordinates of your POIs.
    e) Run master.py on all profiles to generate simulations.
    f) Use post.py to compile the results into a file similar to the example file factors_all
