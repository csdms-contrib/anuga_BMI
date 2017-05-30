#! /usr/bin/env python
import warnings

import numpy as np

import anuga


class AnugaSolver(object):

    def __init__(self, params):
                
        self._domain_shape = str(params['domain_shape'])
        self._shape = tuple(params['shape'])
        self._size = tuple(params['size'])
        self._outline_filename = str(params['outline_filename'])
        self._elevation_filename = str(params['elevation_filename'])
        self._output_filename = str(params['output_filename'])
        self._time_step = float(params['timestep'])
        self._bdry_tags = dict(params['boundary_tags'])
        self._bdry_conditions = dict(params['boundary_conditions'])
        self._max_triangle_area = float(params['maximum_triangle_area'])
        self._stored_quantities = dict(params['stored_quantities'])
        
        self._time = 0
        

        self.initialize_domain()
        self.set_boundary_conditions()
        self.set_other_domain_options()                           
        
        
        # store initial elevations for differencing as array of zeros
        self._land_surface__initial_elevation = np.zeros_like(self.land_surface__elevation)
        
        
        
        
    def initialize_domain(self):
        """Initialize anuga domain"""

        if self._domain_shape[:6] in ['square', 'rectan']:
        
            # finds square and both rectangle and rectangular
            self.domain = anuga.rectangular_cross_domain(
                                self._shape[0],
                                self._shape[1],
                                len1 = self._size[0],
                                len2 = self._size[1])
                                
            # set some default values for quantities
            self.domain.set_quantity('elevation', lambda x,y: -x/2. + 4)
                       
                       
                                
                                
        elif self._domain_shape in ['outline', 'irregular']:
        
            bounding_polygon = anuga.read_polygon(self._outline_filename)
            filename_root = self._elevation_filename[:-4]
            
            
            if self._elevation_filename[-4:] == '.asc':
                anuga.asc2dem(filename_root + '.asc')
                anuga.dem2pts(filename_root + '.dem')
                
            elif self._elevation_filename[-4:] != '.pts':
                assert False, ("Cannot recognize file type of elevation file '%s'. "
                               "Please use .asc or .pts file")
                               
            # generalize the mesh creation to be able to use the sed transport operator
            evolved_quantities =  ['stage', 'xmomentum', 'ymomentum', 'concentration']
            
            anuga.pmesh.mesh_interface.create_mesh_from_regions(
                                bounding_polygon = bounding_polygon,
                                boundary_tags = self._bdry_tags,
                                maximum_triangle_area = self._max_triangle_area)
                                
            self.domain = anuga.Domain(filename_root + '.msh',
                                       evolved_quantities = evolved_quantities)
            
            
            
            self.domain.set_quantity('elevation', filename = filename_root + '.pts')
            
            
        else:
            assert False, ("domain shape must be 'square'/'rectangle'/'rectangular' "
                            "or 'outline'/'irregular'")
                            
    
        self.domain.set_quantity('stage', expression='elevation + %f' % -0.4)
        
        
        
        
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
                
        
        self._bdry_conditions = _bdry_conditions        
        self.domain.set_boundary(self._bdry_conditions)
        
        

    def set_other_domain_options(self):
    
        self.domain.set_name(self._output_filename)
        self.domain.set_quantities_to_be_stored(self._stored_quantities)                
        

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


    ########
    
    @property
    def manning_n_parameter(self):
        """Manning's friction parameter"""
        return self.domain.quantities['friction'].centroid_values
        
    @manning_n_parameter.setter
    def manning_n_parameter(self, new_friction):
        self.domain.set_quantity('friction', new_friction)

    @property
    def water_surface__elevation(self):
        """Temperature values on the grid."""
        return self.domain.quantities['stage'].centroid_values

    @water_surface__elevation.setter
    def water_surface__elevation(self, new_stage):
        self.domain.set_quantity('stage', new_stage)

    @property
    def land_surface__elevation(self):
        return self.domain.quantities['elevation'].centroid_values
        
    @land_surface__elevation.setter
    def land_surface__elevation(self, new_elev):
        self.domain.set_quantity('elevation', new_elev)

        

    #########
    
    @property
    def land_surface__initial_elevation(self):
        """Initial surface elevation, for differencing"""
        return self._land_surface__initial_elevation
        
    @land_surface__initial_elevation.setter
    def land_surface__initial_elevation(self, new_init_elev):
        """Able to set the initial land surface elevation to
        set an initial elev for differencing. Use:
            
        land_surface__initial_elevation = land_surface__elevation
        """
        self._land_surface__initial_elevation[:] = new_init_elev
    

    def update(self):
        """Evolve."""
        
        for t in self.domain.evolve(finaltime = self._time):
            print self.domain.timestepping_statistics()

