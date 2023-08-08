# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 09:07:30 2023

@author: ardya
"""
import numpy as np
import performancesizing as pf
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
import scipy.optimize as opt

# Air density calculation below 11 000 m
while True:    
    try:
        deltaT = float(input('Please enter the temperature difference from standard (15 C) : '))
        break
    except ValueError:
        print('Value must be a number.')
    except AssertionError:
        print('Value must be a scalar.')

while True:
    try:
        altitude = float(input('Please enter the desired runway altitude in ft : ')) * .3048
        assert  0 <= altitude <= 33000
        break
    except AssertionError:
        print('Altitude must be between 0 and 33000 ft')
    except ValueError:
        print('Value must be a number.')

rho, rho0, sigma = pf.AirDensity(altitude, deltaT)

# set W/P values for matching chart
W_P = np.linspace(1, 50, num=50)
W_S = np.linspace(1, 50, num=50)    

# Wing loading calculation for moderate aspect ratio (4 - 8)
Vs = float(input('Please enter the desired stall speed in knots : ')) * 1.687664
sweepangle = float(input('Please enter the intended sweep angle of the wing in degrees : '))
print('\nTypical values for Clmax')
print('Plain wing with no flap = 1.5')
print('Wing with plain flap = 1.8')
print('Wing with slotted flap = 2.2')
print('Wing with fowler flap = 2.5')
print('Wing with double slotted flap = 2.7')
print('Wing with double slotted flap and slat = 3.0')
print('Wing with triple slotted flap and slat = 3.4')
Clmax = float(input('\nPlease enter the Clmax based on above values: '))
CLmax = 0.9 * Clmax * np.cos(np.radians(sweepangle))

plt.figure()
plt.axis([0, 50, 0, 50])
StallConstraint = pf.StallWingLoading(altitude, deltaT, Vs, CLmax)
plt.vlines(StallConstraint, 0, max(W_P), path_effects=[patheffects.withTickedStroke(angle=-135)])
def constraint1(x):
    return (StallConstraint - x[0])

CLTO = CLmax/1.21
TOP = pf.TOP()
TakeoffConstraint = pf.TakeoffWingLoading(TOP, altitude, deltaT, CLTO, W_S)
plt.plot(TakeoffConstraint, W_P, path_effects=[patheffects.withTickedStroke(angle=-135)])
def constraint2(x):
    return (pf.TakeoffWingLoading(TOP, altitude, deltaT, CLTO, x[0]) - x[1])

Slanding = float(input("\nEnter desired landing distance in m : ")) * 3.28084 # converted to ft
Sa = 450 # STOL, 7-deg glideslope
LandingConstraint = pf.LandingWingLoading(Slanding, Sa, altitude, deltaT, CLmax)
plt.vlines(LandingConstraint, 0, max(W_P), path_effects=[patheffects.withTickedStroke(angle=-135)])
def constraint3(x):
    return LandingConstraint - x[0]

AR = 5
e = 0.8
CD0 = .02

ServiceCeiling = float(input("\nEnter desired service ceiling altitude in ft : ")) * 0.3048
Vcruise = float(input("\nEnter desired cruise speed at service ceiling altitude in kts : ")) * 1.687664
CeilingConstraint = pf.CeilingWingLoading(ServiceCeiling, Vcruise, AR, e, CD0, W_S)
plt.plot(W_P, CeilingConstraint, path_effects=[patheffects.withTickedStroke(angle=135)])

def constraint4(x):
    return ((pf.CeilingWingLoading(ServiceCeiling, Vcruise, AR, e, CD0, x[0])) - x[1])

def objective_function(x):
    return -np.sqrt((x[0])**2 + (x[1])**2)

# Initial guess of optimum coordinate
x0 = np.array([25.0, 25.0])
z_opt = opt.fmin_slsqp(objective_function, x0, ieqcons=(constraint1, constraint2, constraint3, constraint4), bounds=[(1.0, 50.0), (1.0, 50.0)])

# Print and plot the result of the optimization
print("Optimal values of W/S and W/P are : ", z_opt)

plt.plot(z_opt[0], z_opt[1], 'ro')  # Mark the minimum with a red circle
plt.xlabel('Wing Loading - lb/ft2')
plt.ylabel('Power Loading - lb/hp')