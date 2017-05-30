#! /usr/bin/env python
import warnings

import numpy as np

import anuga


class AnugaSolver(object):

#     def __init__(self,
#                 domain_shape = 'square',
#                 shape = (10.,5.),
#                 size = (10.,5.),
#                 friction = 0.,
#                 outline_filename = None,
#                 elevation_filename = None,
#                 output_filename = 'anuga_output',
#                 output_timestep = 10,
#                 timestep = 1,
#                 boundary_tags = None,
#                 boundary_conditions = {'left': 'Reflective',
#                                        'right': ['Dirichlet', 5, 0, 0],
#                                        'top': 'Reflective',
#                                        'bottom': 'Reflective'},
#                 maximum_triangle_area = 10):

    def __init__(self, params):
                
        self._domain_shape = str(params['domain_shape'])
        self._shape = tuple(params['shape'])
        self._size = tuple(params['size'])
        self._friction = float(params['friction'])
        self._outline_filename = str(params['outline_filename'])
        self._elevation_filename = str(params['elevation_filename'])
        self._output_filename = str(params['output_filename'])
        self._output_time_step = float(params['output_timestep'])
        self._time_step = float(params['timestep'])
        self._bdry_tags = list(params['boundary_tags'])
        self._bdry_conditions = dict(params['boundary_conditions'])
        self._maximum_triangle_area = float(params['maximum_triangle_area'])
        
        self._time = 0
        
        
        
        self.initialize_domain()
        self._bdry_conditions = self.set_boundary_conditions()
        self.domain.set_boundary(self._bdry_conditions)
                                       

        self.domain.set_quantity('elevation', lambda x,y: -x/2. + 4)
        self.domain.set_quantity('stage', -0.4)
        self.domain.set_quantity('friction', self._friction)
        
        
        self._water_surface__elevation = self.domain.quantities['stage'].centroid_values
        self._land_surface__elevation = self.domain.quantities['elevation'].centroid_values
        
        
        # store initial elevations for differencing
        self._land_surface__initial_elevation = self._land_surface__elevation.copy()



    def set_boundary_conditions(self):
        """
        Set boundary conditions for ANUGA domain
        
        Valid boundaries are (case insensitive):
        - reflective
        - transmissive
        - dirichlet / fixed (must specify stage at this boundary)
        - time (need to specify a lambda function)
        
        TODO:
        - check possible failure modes (how would anuga normally fail if the boundaries
            are not specified correctly?)
        - add defaults if not enough boundaries are specified
        - fail if receives an unknown boundary type
        - accept other inputs for time boundary (file?)
        """
        
        _bdry_conditions = {}
        
        for key, value in self._bdry_conditions.iteritems():

            if isinstance(value, str):
                value = [value]
        
            bdry_type = value[0]
            
            if bdry_type.lower() == 'reflective':
                _bdry_conditions[key] = anuga.Reflective_boundary(self.domain)
                
                
                
            elif bdry_type.lower() == 'transmissive':
                _bdry_conditions[key] = anuga.Transmissive_boundary(self.domain)
                
                
                
            elif bdry_type.lower() in ['dirichlet', 'fixed']:
            
                dirichlet_vals = value[1:]
                
                assert len(value) > 1, ("Need to specify stage of "
                                        "Dirichlet boundary '%s'" % key)
                
                if len(dirichlet_vals) == 1: dirichlet_vals += [0., 0.]
                    
                _bdry_conditions[key] = anuga.Dirichlet_boundary(dirichlet_vals)
                
                
                
            elif bdry_type.lower() == 'time':
            
                assert len(value) > 1, ("Need to specify lambda function for "
                                        "Time boundary '%s'" % key)
                
                _bdry_conditions[key] = anuga.Time_boundary(domain = domain,
                                                                 function = value[1])
                
            else:
            
                assert False, ("Did not recognize boundary type '%s' "
                               "of boundary '%s'" % (bdry_type, key))
                
                
                
        return _bdry_conditions



    def initialize_domain(self):
        """Initialize anuga domain"""

        if self._domain_shape[:6] in ['square', 'rectan']:
        
            # finds square and both rectangle and rectangular
            self.domain = anuga.rectangular_cross_domain(
                                self._shape[0],
                                self._shape[1],
                                len1 = self._size[0],
                                len2 = self._size[1])
                                
        elif self._domain_shape in ['outline', 'irregular']:
            pass
            
        else:
            assert False, ("domain shape must be 'square'/'rectangle'/'rectangular' "
                            "or 'outline'/'irregular'")
                
        

    @property
    def grid_x(self):
        """x position of centroids"""
        var_values = self.domain.quantities['x'].centroid_values
        return var_values
        
    @property
    def grid_y(self):
        """y position of centroids"""
        var_values = self.domain.quantities['y'].centroid_values
        return var_values
        
    @property
    def grid_z(self):
        """z position of centroids"""
        return self.land_surface__elevation()

    @property
    def time_step(self):
        """The time step."""
        return self._time_step

    @time_step.setter
    def time_step(self, new_dt):
        self._time_step = new_dt

    @property
    def shape(self):
        """Number of grid rows and columns."""
        return self._shape

    @property
    def size(self):
        """Size of grid in meters."""
        return self._size

    @property
    def stage(self):
        """Upstream stage."""
        return self._stage

    ########

    @property
    def water_surface__elevation(self):
        """Temperature values on the grid."""
        return self._water_surface__elevation

    @water_surface__elevation.setter
    def water_surface__elevation(self, new_stage):
        self._water_surface__elevation[:] = new_stage

    @property
    def land_surface__elevation(self):
        return self._land_surface__elevation
        
    @land_surface__elevation.setter
    def land_surface__elevation(self, new_elev):
        self._land_surface__elevation[:] = new_elev


    #########

    def update(self):
        """Evolve."""
        
#         self.domain.set_evolve_starttime(self._time)
        
        for t in self.domain.evolve(finaltime = self._time + self._time_step):
            print self.domain.timestepping_statistics()
        
        self.water_surface__elevation[:] = self.domain.quantities['stage'].centroid_values
        # 
        print self.water_surface__elevation.mean()
