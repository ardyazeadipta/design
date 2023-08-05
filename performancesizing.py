# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 09:20:54 2023

@author: ardya
"""

import numpy as np
from scipy.optimize import curve_fit

def AirDensity(altitude, deltaT):
    """
    Function to calculate air density at a given temperature difference and altitude.
    Limited to altitudes between 0 and 11000m or 33000ft.

    Parameters
    ----------
    altitude : float
        Altitude of reference in m.
    deltaT : float
        Difference in sea level temperature from ISA standard of 15 degrees C.

    Returns
    -------
    rho0 : float
        Air density on sea level in kg/m3.
    rho : float
        Air density on altitude of reference in kg/m3.
    sigma : float
        Ratio between rho and rho0.

    """
    T0 = 288.15 + deltaT
    lapserate = 6.5/1000 # lapse rate of normal troposphere air in K/1000 m
    rho0 = 1.225  # air density on sea level in kg/m3
    g = 9.80665 # m/s2
    R = 287.053 # J/kgK 
    
    sigma = (1 - lapserate/T0*altitude)**(g/(R*lapserate))
    
    rho = sigma * rho0
    return rho0, rho, sigma

def StallWingLoading(altitude, Vs, CLmax):
    """
    Function to calculate the wing loading of the aircraft based on its intended stall speed and altitude.

    Parameters
    ----------
    altitude : float
        Altitude of flight in ft.
    Vs : float
        Stall speed of the aircraft in ft/s.
    CLmax : float
        Maximum lift coefficient of the wing.

    Returns
    -------
    W_Sstall : float
        Wing loading of the aircraft in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(altitude, 0)
    rho = rho * 0.0019403203 # convert from kg/m3 to slug/ft3
    q = .5 * rho * Vs**2
    
    W_Sstall =  q * CLmax
    return W_Sstall

def TOP():
    """
    Function to calculate takeoff parameter based on takeoff criteria and distance from input.

    Returns
    -------
    float
        Takeoff parameter.

    """
    # Load TOP data
    TOP_data = np.genfromtxt('TOP.csv', delimiter=',', skip_header=1, invalid_raise=False)

    # Extract data
    TO_Parameter = TOP_data[:,0]
    TO_Dist_Prop_GroundRoll = TOP_data[:,1] * 1000
    TO_Dist_Prop_50ft = TOP_data[:,2] * 1000
    TO_Dist_Jet_GroundRoll = TOP_data[:,3] * 1000
    TO_Dist_Jet_50ft = TOP_data[:,4] * 1000
    TO_Dist_Jet_2eng_BFL = TOP_data[:,5] * 1000
    TO_Dist_Jet_3eng_BFL = TOP_data[:,6] * 1000
    TO_Dist_Jet_4eng_BFL = TOP_data[:,7] * 1000

    print('\nTO_Dist_Prop_GroundRoll')
    print('TO_Dist_Prop_50ft')
    print('TO_Dist_Jet_GroundRoll')
    print('TO_Dist_Jet_50ft')
    print('TO_Dist_Jet_2eng_BFL')
    print('TO_Dist_Jet_3eng_BFL')
    print('TO_Dist_Jet_4eng_BFL')
    criteria = input('\nCopy the takeoff criteria from the list above : ')
    distance = float(input('\nEnter the desired takeoff distance or balanced field length in m : ')) * 3.28084

    def valid_indices(criteria):
        return np.nonzero(~np.isnan(criteria))

    # Valid indices of this takeoff distance criteria
    criteria_indices = valid_indices(locals()[criteria])

    # Value of valid indices
    x = TO_Parameter[criteria_indices]
    y = locals()[criteria][criteria_indices]
    
    # Define TOP fitting function as quadratic
    def func(y, a, b, c):
        return a * y**2 + b * y + c
    
    # Fit curve to valid data
    popt, pcov = curve_fit(func, y, x)

    # TOP value based on fitted function
    TOP = popt[0] * distance**2 + popt[1] * distance + popt[2]
    return TOP

def TakeoffWingLoading(TOP, altitude, deltaT, CLTO, W_P):
    """
    Function to calculate the required wing loading for takeoff for a given power loading.

    Parameters
    ----------
    TOP : float
        Takeoff parameter.
    altitude : float
        Altitude of runway at takeoff in ft.
    deltaT : float
        Difference in sea level temperature from ISA standard of 15 degrees C.
    CLTO : float
        Lift coefficient at takeoff, typically maximum wing lift coefficient divided by 1.21.
    W_P : float or array of floats
        Power loading of the aircraft in lb/hp.

    Returns
    -------
    W_Stakeoff : float or array of floats
        Wing loading required for takeoff requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(altitude, deltaT)
    
    W_Stakeoff = TOP * sigma * CLTO * (1/W_P)
    return W_Stakeoff

def LandingWingLoading(Slanding, Sa, altitude, deltaT, CLmax):
    """
    Function to calculate wing loading required for a given landing and approach distance.

    Parameters
    ----------
    Slanding : float
        Required landing distance to a complete stop in ft, includes clearing a 50-ft obstacle.
    Sa : float
        Obstacle-clearance distance in ft, varies from 450ft to 1000ft depending on the aircraft type.
    altitude : float
        Altitude of runway at landing in ft.
    deltaT : float
        Difference in sea level temperature from ISA standard of 15 degrees C.        
    CLmax : float
        Maximum lift coefficient of the wing.

    Returns
    -------
    W_Slanding : float
        Wing loading required for landing requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(altitude, deltaT)
    
    W_Slanding = (Slanding - Sa) * sigma * CLmax / 80
    return W_Slanding

def CruiseWingLoading(altitude, Vcruise, AR, e, CD0):
    """
    Function to calculate wing loading required to maximize cruise range in a given cruise speed.

    Parameters
    ----------
    altitude : float
        Altitude at which cruise is performed in ft.
    rho : float
        Air density at an altitude of reference in slug/ft3.
    Vc : float
        Aircraft intended cruise speed in ft/s.
    AR : float
        Aircraft wing aspect ratio.
    e : float
        Oswald span efficiency factor, approximately 0.6 to 0.8 for fighter, and 0.8 for other aircraft.
    CD0 : float
        Zero-lift drag coefficient, approximately 0.015 for jet, 0.02 for clean propeller, 0.03 for fixed gear propeller.

    Returns
    -------
    W_Scruise : float
        Wing loading required for cruise requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(altitude, 0)
    rho = rho * 0.0019403203 # convert from kg/m3 to slug/ft3
    q = 0.5 * rho * Vcruise**2
    
    W_Scruise = q * (np.pi*AR*e*CD0)**0.5
    return W_Scruise

def LoiterWingLoading(altitude, Vloiter, AR, e, CD0):
    """
    Function to calculate wing loading required to optimize loiter/minimum power required in a given loiter speed.
    
    Parameters
    ----------
    altitude : float
        Altitude at which loiter is performed in ft.
    rho : float
        Air density at an altitude of reference in slug/ft3.
    Vc : float
        Aircraft intended cruise speed in ft/s.
    AR : float
        Aircraft wing aspect ratio.
    e : float
        Oswald span efficiency factor, approximately 0.6 to 0.8 for fighter, and 0.8 for other aircraft.
    CD0 : float
        Zero-lift drag coefficient, approximately 0.015 for jet, 0.02 for clean propeller, 0.03 for fixed gear propeller.

    Returns
    -------
    W_Sloiter : float
        Wing loading required for loiter requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(altitude, 0)
    rho = rho * 0.0019403203 # convert from kg/m3 to slug/ft3
    q = 0.5 * rho * Vloiter**2
    
    W_Sloiter = q * (3*np.pi*AR*e*CD0)**0.5
    return W_Sloiter

def InstantTurnWingLoading(altitude, turnrate, Vcorner, CLmaxcombat):
    """
    Function to calculate wing loading to meet a given instant turn rate requirement at a given altitude and speed.

    Parameters
    ----------
    altitude : float
        Altitude at which combat/turn is performed in ft.
    turnrate : float
        Turn rate of the aircraft in rad/s.
    Vcorner : float
        Speed at which the maximum lift available exactly equals the allowable load factor.
    CLmaxcombat : float
        Maximum lift coefficient at combat conditions, about 0.6 - 0.8 for simple fighter, 1.0 - 1.5 for complex fighter.

    Returns
    -------
    W_Sinstantturn : float
        Wing loading required for instant turn rate requirements in lb/ft2.

    """
    g = 32.15223 # ft/s2
    rho0, rho, sigma = AirDensity(altitude, 0)
    rho = rho * 0.0019403203 # convert from kg/m3 to slug/ft3
    q = 0.5 * rho * Vcorner**2
    n = ((turnrate*Vcorner/g)**2 + 1)**0.5
    
    W_Sinstantturn = q * CLmaxcombat / n
    return W_Sinstantturn

def SustainedTurnWingLoading(altitude, Vturn, n, AR, e, CD0, W_P):
    """
    Function to calculate wing loading related to sustained turn requirements for a given altitude, speed, and load factor.

    Parameters
    ----------
    altitude : float
        Altitude at which combat/turn is performed in ft.
    Vturn : float
        Speed at which combat/turn is performed in ft/s.
    n : float
        Load factor to be sustained during turn.
    AR : float
        Aircraft wing aspect ratio.
    e : float
        Oswald span efficiency factor, approximately 0.6 to 0.8 for fighter, and 0.8 for other aircraft.
    CD0 : float
        Zero-lift drag coefficient, approximately 0.015 for jet, 0.02 for clean propeller, 0.03 for fixed gear propeller.
    W_P : float
        Power loading, in lb/hp.

    Returns
    -------
    W_Ssustainedturn : float
        Wing loading required for sustained turn requirements in lb/ft2.
        
    """
    rho0, rho, sigma = AirDensity(altitude, 0)
    q = 0.5 * rho * Vturn**2
    propeff = .8 # propeller efficiency assumed 0.8
    T_W = 550 * propeff/Vturn * 1/W_P
    
    W_Ssustainedturn = (T_W + (T_W**2 - (4*n**2*CD0/(np.pi*AR*e))**.5)/(2*n**2/(q*np.pi*AR*e)))
    return W_Ssustainedturn

def ClimbWingLoading(G, Vclimb, AR, e, CD0, W_P):
    """
    Function to calculate wing loading required to satisfy climb gradient in a given horizontal speed.

    Parameters
    ----------
    G : float
        Ratio between vertical and horizontal speed or climb gradient. Positive value for climb, negative value for glide.
    Vclimb : float
        Horizontal speed during the climb, in ft/s.
    AR : float
        Aircraft wing aspect ratio.
    e : float
        Oswald span efficiency factor, approximately 0.6 to 0.8 for fighter, and 0.8 for other aircraft.
    CD0 : float
        Zero-lift drag coefficient, approximately 0.015 for jet, 0.02 for clean propeller, 0.03 for fixed gear propeller.
    W_P : float
        Power loading, in lb/hp. Set to zero if calculating glide.

    Returns
    -------
    W_Sclimb : float
        Wing loading required for climb requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(0, 0)
    q = 0.5 * rho * Vclimb**2
    propeff = .8 # propeller efficiency assumed 0.8
    T_W = 550 * propeff/Vclimb * 1/W_P
    
    W_Sclimb = ((T_W - G) + ((T_W - G)**2 - (4*CD0/(np.pi*AR*e))**.5)/(2/(q*np.pi*AR*e)))
    return W_Sclimb

def CeilingWingLoading(altitude, Vceiling, AR, e, CD0, W_P):
    """
    Function to calculate wing loading required to fly at a certain speed and maximum altitude.

    Parameters
    ----------
    altitude : float
        Maximum ceiling altitude, in ft.
    Vceiling : float
        Flight speed at maximum ceiling altitude, in ft/s.
    AR : float
        Aircraft wing aspect ratio.
    e : float
        Oswald span efficiency factor, approximately 0.6 to 0.8 for fighter, and 0.8 for other aircraft.
    CD0 : float
        Zero-lift drag coefficient, approximately 0.015 for jet, 0.02 for clean propeller, 0.03 for fixed gear propeller.
    W_P : float
        Power loading, in lb/hp.

    Returns
    -------
    W_Sceiling : float
        Wing loading required for maximum ceiling requirements in lb/ft2.

    """
    rho0, rho, sigma = AirDensity(0, 0)
    q = 0.5 * rho * Vceiling**2
    propeff = .8 # propeller efficiency assumed 0.8
    G = (100/60) / Vceiling
    T_W = 550 * propeff/Vceiling * 1/W_P
    
    W_Sceiling =  ((T_W - G) + ((T_W - G)**2 - (4*CD0/(np.pi*AR*e))**.5)/(2/(q*np.pi*AR*e)))
    return W_Sceiling

