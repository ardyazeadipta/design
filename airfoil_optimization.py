# -*- coding: utf-8 -*-
"""
Created on Tue May  9 08:34:37 2023

@author: ardya
"""

from aeropy.xfoil_module import call, output_reader, create_input
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om

airfoil_name = 'airfoiltest'
x_array = np.arange(0, 1.01, .01)
x_list = x_array.tolist()
thickness = .15
y_u_array = np.sqrt(thickness**2 - (x_array - 0.5)
                    ** 2 * (thickness**2 / 0.5**2))
y_u_list = y_u_array.tolist()
y_l_array = -y_u_array
y_l_list = y_l_array.tolist()

create_input(x_list, y_u_list, y_l=y_l_list, filename=airfoil_name)
alpha_list = np.arange(start=0, stop=20, step=.5)
reynolds = 1e6
mach = 0
aoa_start = 0.0
aoa_end = max(alpha_list)
n_crit = 9
call(airfoil_name, alfas=alpha_list, output='Polar',
     Reynolds=reynolds, NACA=False, iteration=100, PANE=True,
     NORM=True, )
data = output_reader(
    f'Polar_{airfoil_name}_{reynolds}_{aoa_start}_{aoa_end}', separator='\t', rows_to_skip=10)

L_D = []
for a, b in zip(data['CL'], data['CD']):
    L_D.append(a / b)

L_D_array = np.array(L_D)

plt.plot(x_array, y_u_array)
plt.xlim(0, 1)
plt.ylim(0, 1)
