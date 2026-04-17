
2026-03-26 Sylfest Glimsdal

This cpp program for waveform extraction from HySEA output is written by Andrey Baybeko (GFZ). 
If the version of HySEA is not accepted, try to add your version  of HySEA (as written in the outputfile) in the code in file cNcHySea.h (very beginning) and cNcHySea_rw.cpp (around line 90).
To compute MIH for HySEA output you need to run the cpp program (postprocess_HySEA) on the output from HySEA
To compile the code try to use the bash script in this folder (see also commented lines for install proper dependencies)