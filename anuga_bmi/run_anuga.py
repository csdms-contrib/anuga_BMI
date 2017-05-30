"""Solve the heat equation of a uniform rectilinear grid.

Solve the heat equation of a rectilinear grid with shape (*GRID_NY*,
*GRID_NX*) and row and column spacing (*GRID_DY*, *GRID_DX*). The thermal
conductivity is given by *ALPHA*.

In cartesian coordinates, the heat equation is the following parabolic
differential equation,

    del u / del t - alpha (del^2 u / del x^2 + del^2 u / del y^2) = 0

This becomes the following finite-difference problem,

    Delta u = alpha Delta t ((u_i-1,j + u_i+1,j) / Delta x^2 +
                             (u_i,j-1 + u_i,j+1) / Delta y^2 -
                             2 u_i,j / (Delta x^2 + Delta y^2))
"""

from __future__ import print_function

import sys
import numpy as np

from bmi_anuga import BmiAnuga

np.set_printoptions(linewidth=120,
                    formatter={'float_kind': lambda x : '%6.4F' % x})


if __name__ == '__main__':
    sww = BmiAnuga()
    sww.initialize('anuga.yaml')

#     grid_id = sww.get_var_grid('water_surface__elevation')
    
#     grid_shape = sww.get_grid_shape(grid_id)


#     stage = sww.get_value('water_surface__elevation')
#     print(stage)
# 
#     sww.set_value('water_surface__elevation', stage + 0.1)
    
#     fp = open('water_surface_elev.txt', 'wb')

    for time in np.linspace(0., 100., 5):
#         print('Time = {time}'.format(time=time))
#         np.savetxt(fp, sww.get_value('water_surface__elevation'),
#                    fmt='%6.4F')
#         print('**', sww.get_value('water_surface__elevation'))

        sww.update_until(time)

#     fp.close()
