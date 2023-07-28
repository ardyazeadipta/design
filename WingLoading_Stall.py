# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 09:07:30 2023

@author: ardya
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patheffects
from airdensity import AirDensity

W_P = np.linspace(0, 1000, 1001)

# Air density calculation below 11 000 m
while True:    
    try:
        deltaT = float(input('Please enter the temperature difference from standard (15 C) : '))
        break
    except ValueError:
        print('Value must be a number.')

while True:
    try:
        altitude = float(input('Please enter the desired altitude in m : '))
        assert altitude >= 0 or altitude >= 11000
        break
    except AssertionError:
        print('Altitude must be between 0 and 11000 m')
    except ValueError:
        print('Value must be a number.')

rho = AirDensity(altitude, deltaT)
   
# Wing loading calculation for moderate aspect ratio (4 - 8)
Vs = float(input('Please enter the desired stall speed in knots : ')) * .5144
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

W_Sstall = .5 * rho * Vs**2 * CLmax
print(f'The required wing loading is <= {W_Sstall:.0f} kg/m2')

plt.vlines(W_Sstall, 0, 1000, path_effects=[
         patheffects.withTickedStroke(angle=-45)])
