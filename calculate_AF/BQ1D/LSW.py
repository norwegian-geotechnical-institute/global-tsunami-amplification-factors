#!/usr/bin/python

import os, sys, getopt, time, numpy, math


##########################################################################    
def solve_timesteps(eta,u,incr,olddepth,newdepth,dt,alpha,eps,timelevels,eta0,u0,rad, kappa):
    """solving at a given number of timelevels"""
    
    for i in range(timelevels):
        eta=solve_eta(eta,u,incr,olddepth,newdepth,dt,alpha,eps,eta0,kappa)
        u=solve_u(eta,u,incr,newdepth,dt,alpha,eps,u0,rad,kappa)
    return eta,u


##########################################################################    
def solve_eta(eta,u,incr,olddepth,newdepth,dt,alpha,eps,eta0,kappa):
    """solving using explicite schemes (LSW) and returning eta"""
    eta[:]=-olddepth[:-1]+newdepth[:-1]+eta[:]-(dt/incr[:])*(newdepth[1:]*u[1:]-newdepth[:-1]*u[:-1])

    if eta0!=0:
        eta[0]=eta0
    return eta


##########################################################################    
def solve_u(eta,u,incr,depth,dt,alpha,eps,u0,rad,kappa):
    """solving using explicit schemes (LSW) returning u"""

    u[0]=u0
    if rad:
        u[-1]=eta[-1]*math.sqrt(1/(depth[-1]))
    else:
        u[-1]=0
    u[1:-1]=u[1:-1]-2*dt*(eta[1:]-eta[:-1])/(incr[1:]+incr[:-1])

    return u

  