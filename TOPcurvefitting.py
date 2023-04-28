# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 14:38:18 2023

@author: ardya
"""
import numpy as np
from scipy.optimize import curve_fit


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
criteria = input('Copy the takeoff criteria from the list above :')
distance = float(input('Enter the desired takeoff distance in feet: '))

def valid_indices(criteria):
    return np.nonzero(~np.isnan(criteria))

# Valid indices of this takeoff distance criteria
criteria_indices = valid_indices(locals()[criteria])

# Value of valid indices
x = TO_Parameter[criteria_indices]
y = locals()[criteria][criteria_indices]

# Fit curve to valid data
popt, pcov = curve_fit(func, y, x)

# TOP value based on fitted function
TOP = popt[0] * distance**2 + popt[1] * distance + popt[2]