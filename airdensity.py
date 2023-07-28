# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 09:20:54 2023

@author: ardya
"""
def AirDensity(altitude, deltaT):
    """
    Function to calculate air density calculation below 11 000 m altitude
    
    altitude in meters and deltaT in K or C
    
    """
    
    T0 = 288.15 + deltaT
    lapserate = 6.5/1000 # K/m
    rho0 = 1.225 # kg/m3
    g = 9.80665 # m/s2
    R = 287.053 # J/kgK 
    sigma = (1 - lapserate/T0*altitude)**(g/(R*lapserate))
    rho = sigma * rho0
    return rho

rho = AirDensity(10, -15.0)