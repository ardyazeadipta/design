# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 07:55:46 2023

@author: ardya
"""

import pandas as pd
import openmdao.api as om
import numpy as np
from PIL import Image
import math
from scipy.optimize import curve_fit

### Weight Estimation ###

# Specific Fuel Consumption
V_cruise = float(input("Enter cruise speed in knots: ")) * 1.687664
V_loiter = float(input("Enter loiter speed in knots: ")) * 1.687664

Engine_type = input('What type of engine will be used (jet/prop)? ')
print('')

while Engine_type != 'jet' or Engine_type != 'prop':
    if Engine_type == 'jet':
        sfc_data = pd.read_excel(
            'SizingData.xlsx', 'SpecificFuelConsumption_Jet', header=0, index_col=0)
        for i in sfc_data.index:
            print(f'{i}')
        Engine_type_index = input('Copy the engine from the list above: ')
        C_cruise = sfc_data['Cruise'][Engine_type_index] / 3600
        C_loiter = sfc_data['Loiter'][Engine_type_index] / 3600
        break
    elif Engine_type == 'prop':
        sfc_data = EmptyWeightFraction = pd.read_excel(
            'SizingData.xlsx', 'SpecificFuelConsumption_Prop', header=0, index_col=0)
        for i in sfc_data.index:
            print(f'{i}')
        Engine_type_index = input('Copy the engine from the list above: ')
        C_cruise = sfc_data['Cruise'][Engine_type_index] * \
            V_cruise / (550 * .8) / 3600
        C_loiter = sfc_data['Loiter'][Engine_type_index] * \
            V_loiter / (550 * .8) / 3600
        break
    else:
        Engine_type = input('What type of engine will be used (jet/prop)? ')

# L/D estimation
AR = float(input('\nChoose an aspect ratio: '))
print('')
K_LD_data = pd.read_excel('SizingData.xlsx', 'K_LD', header=0, index_col=0)
for i in K_LD_data.index:
    print(f'{i}')
K_LD_index = input(
    'Copy the most suitable configuration from the list above: ')
image = Image.open("WettedAreaRatio.jpg")
image.show()

WettedAreaRatio = float(
    input('\nEstimate the wetted area ratio of the aircraft using image shown: '))

L_D_max = K_LD_data['K_LD'][K_LD_index] * (AR / WettedAreaRatio) ** 0.5

if Engine_type == 'jet':
    L_D_cruise = 0.866 * L_D_max
    L_D_loiter = L_D_max
else:
    L_D_cruise = L_D_max
    L_D_loiter = 0.866 * L_D_max

# Mission profile construction

mission_segments = []
segment_weights = []
segment = ""

print("\nEnter mission segments (takeoff, climb, cruise, loiter, land)\n(type 'stop' to end):")
while segment != "stop":
    segment = input("Enter mission segment: ")
    if segment != "stop":
        if segment == "takeoff":
            weight = 0.97
        elif segment == "climb":
            weight = 0.985
        elif segment == "loiter":
            E = float(input('Enter the duration of loiter in hours: ')) * 3600
            weight = math.exp((-E * C_loiter) / L_D_loiter)
        elif segment == "land":
            weight = 0.995
        elif segment == "cruise":
            R = float(
                input("Enter range of cruise in nautical miles: ")) * 6076.115
            weight = math.exp(-(R * C_cruise) / (V_cruise * L_D_cruise))

        mission_segments.append(segment)
        segment_weights.append(weight)

print("\nMission Profile:")
for i, segment in enumerate(mission_segments):
    print(f"{i+1}. {segment}: {segment_weights[i]:.2f}")

total_fuel_fraction = 1
for weight in segment_weights:
    total_fuel_fraction *= weight
total_fuel_fraction = 1 - total_fuel_fraction
print(f"\nTotal Fuel Fraction: {total_fuel_fraction:.2f}")


# Empty weight fraction estimation
EmptyWeightFraction = pd.read_excel(
    'SizingData.xlsx', 'EmptyWeightFraction', header=0, index_col=0)
W_crew = float(input('\nEnter the weight of the crew in lbs: '))
W_payload = float(input('Enter the weight of the payload in lbs: '))
print('')

for i in EmptyWeightFraction.index:
    print(f'{i}')
AC_type = input('Copy the type of aircraft from the list above : ')
VariableSweep = input('Variable sweep (y/n)? ')
Kvs = 1.04 if VariableSweep == 'y' else 1
W0_guess = float(
    input('Enter the estimated takeoff weight in lbs (higher numbers are better):'))
We_W0 = EmptyWeightFraction['A'][AC_type] * \
    (W0_guess ** EmptyWeightFraction['C'][AC_type]) * Kvs
W0_calc = (W_crew + W_payload) / (1 - total_fuel_fraction - We_W0)

while abs(W0_guess - W0_calc) > 1:
    W0_guess -= (W0_guess - W0_calc)
    We_W0 = EmptyWeightFraction['A'][AC_type] * \
        (W0_guess ** EmptyWeightFraction['C'][AC_type]) * Kvs
    W0_calc = (W_crew + W_payload) / (1 - total_fuel_fraction - We_W0)
    if abs(W0_guess - W0_calc) <= 1:
        break

We = We_W0 * W0_guess

print(f'\nThe takeoff weight of the aircraft is {W0_guess:.0f} lbs.')
print(f'The empty weight of the aircraft is {We:.0f} lbs.')

### Wing loading and power loading ###
## Stall Speed ##


## Takeoff Distance ##
# Define TOP fitting function as quadratic
def func(y, a, b, c):
    return a * y**2 + b * y + c

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

print('TO_Dist_Prop_GroundRoll')
print('TO_Dist_Prop_50ft')
print('TO_Dist_Jet_GroundRoll')
print('TO_Dist_Jet_50ft')
print('TO_Dist_Jet_2eng_BFL')
print('TO_Dist_Jet_3eng_BFL')
print('TO_Dist_Jet_4eng_BFL')
criteria = input('Copy the takeoff criteria from the list above: ')
distance = float(input('Enter the desired takeoff distance in feet: '))

def valid_indices(x):
    return np.nonzero(~np.isnan(x))

# Valid indices of this takeoff distance criteria
criteria_indices = valid_indices(locals()[criteria])

# Value of valid indices
x = TO_Parameter[criteria_indices]
y = locals()[criteria][criteria_indices]

# Fit curve to valid data
popt, pcov = curve_fit(func, y, x)

# TOP value based on fitted function
TOP = popt[0] * distance**2 + popt[1] * distance + popt[2]