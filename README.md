# global-tsunami-amplification-factors
Global tsunami amplification factors used for estimation of tsunami run-up, based on wave input from offshore mariograms. By extracting the height of the heighest wave from a given mariogram, you will find a proper amplification factor for estimate the tsunami run-up based on the shape (leading trough - negative polarity named "neg" og leading peak - positive polarity "pos") and the wave periode (120-3600s). See documentation in the paper Glimsdal_etal_ampfactos_paper.pdf.

In the file global_ampf_v01.txt there is a collection of  amplification factors at totally xxxxx points globally. The amplification factors are produced based on wave simulations along transects on local bathymetry. Each line of the file contain all information for a given point of the form:

globalid lon lat neg af120 af200 af300 af600 af1000 af1800 af3600 pos af120 af200 af300 af600 af1000 af1800 af3600 prof name area prev

where globalid is a unique identification for each point, lon and lat is the location in geographical coordinates. If the wave signal in the mariogram is haveing a leading trough (negative polarity), the values af120-af3600 after the flag "neg" must be used. For a leading peak (positive polarity) the values follows after the flag "pos". The amplification factors are a combination of simulation along transects based on idealized og real bathymetry indicated by the column "prof". To extract points for a region, there is a possibility search the to use areas specified in the column "areas". 
