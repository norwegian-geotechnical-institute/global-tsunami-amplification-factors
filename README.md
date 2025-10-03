# global-tsunami-amplification-factors
Global tsunami amplification factors used for estimation of tsunami run-up, based on wave input from offshore mariograms. By extracting the height of the heighest wave from a given mariogram, you will find a proper amplification factor for estimate the tsunami run-up based on the shape (leading trough - negative polarity named "neg" og leading peak - positive polarity "pos") and the wave periode (120-3600s). See documentation in the paper Glimsdal_etal_ampfactos_paper.pdf.

In release v3.0.0 software for both calculating your own amplification factors (folder calculate_AF) and extracting MIH from your own simulations (folder calculate_MIH) including tools for HySEA is now added. Check folders for example files and README.txt files for instructions. 

In the file ampfactors/global_ampf_v04.txt there is a collection of  amplification factors at totally 17841 points globally. The amplification factors are produced based on wave simulations along transects on local bathymetry, mostly on idealized profiles. Each line of the file contain all information for a given point of the form:

globalid lon lat neg af120 af200 af300 af600 af1000 af1800 af3600 pos af120 af200 af300 af600 af1000 af1800 af3600 prof name area prev

where "globalid" is a unique identification for each point, "lon" and "lat" is the location in geographical coordinates. If the wave signal in the mariogram is having a leading trough (negative polarity), the values "af120"-"af3600" (depending on the wave period in seconds) after the flag "neg" must be used. For a leading peak (positive polarity) the values follows after the flag "pos". The amplification factors are a combination of simulation along transects based on idealized and real bathymetry indicated by the column "prof". To extract points for a region, there is a possibility search by filtering areas specified in the column "areas". 

All releases of the global tsunami amplification factors is permanently archived on Zenodo with DOI https://zenodo.org/doi/10.5281/zenodo.10732727

AmpFact is one of the services included in the GEO-INQUIRE Virtual Access to the next generation of software as a service (VA4-532-2).
(see https://www.geo-inquire.eu/virtual-access/software for details.)
 
![GEO-INQUIRE project logo](Geo-INQUIRE_logo_small.png)

