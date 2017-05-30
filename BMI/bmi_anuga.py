#! /usr/bin/env python
"""Basic Model Interface implementation for anuga."""

import types

import numpy as np
import yaml
from basic_modeling_interface import Bmi

from anuga_solver import AnugaSolver


class BmiAnuga(Bmi):


    _name = 'ANUGA'
    _input_var_names = ('water_surface__elevation',)
    _output_var_names = ('water_surface__elevation',)

    def __init__(self):
        """Create a BmiAnuga model that is ready for initialization."""
        self._anuga = None
        self._time = 0.
        self._values = {}
        self._var_units = {}
        self._grids = {}
        self._grid_type = {}

    def initialize(self, filename='anuga.yaml'):
        """Initialize the ANUGA model.

        Parameters
        ----------
        filename : str, optional
            Path to name of input file.
        """
        
        with open(filename, 'r') as file_obj:
            params = yaml.load(file_obj)
        
        default_params = {'domain_shape':'square',
                          'shape':(10.,5.),
                          'size':(10.,5.),
                          'friction':0.,
                          'outline_filename':None,
                          'elevation_filename':None,
                          'output_filename':'anuga_output',
                          'output_timestep':10,
                          'timestep':1,
                          'boundary_tags':['left', 'right', 'top', 'bottom'],
                          'boundary_conditions':{'left': 'Reflective',
                                       'right': ['Dirichlet', 5, 0, 0],
                                       'top': 'Reflective',
                                       'bottom': 'Reflective'},
                          'maximum_triangle_area':10}
        
        
        
        for key,value in default_params.items():
            params[key] = params.get(key, default_params[key])

        for key,value in params.items():
            if (value is None) or (value == 'None'):
                params[key] = default_params[key]

        if params['domain_shape'] == 'square':
            assert (set(params['boundary_conditions'].keys()) ==
                    set(['left', 'right', 'top', 'bottom'])), (
                    "The boundary names for square domains must be "
                    "'left', 'right', 'top', and 'bottom'. Check that your "
                    "boundary conditions use those names.")
        
        if params['domain_shape'] == 'outline':
            assert (set(params['boundary_conditions'].keys()) ==
                    set(params['boundary_tags'].keys())), (
                    "The boundary tag names don't match the boundary "
                    "condition names. Check that the two dictionaries use "
                    "the same boundary names.")
                    
                    
            
        self._anuga = AnugaSolver(params)


        self._values = {
            'water_surface__elevation': self._anuga.water_surface__elevation,
            'land_surface__elevation': self._anuga.land_surface__elevation,
            'manning_n_parameter': self._anuga.manning_n_parameter,
            'land_surface__initial_elevation': self._anuga.land_surface__initial_elevation,
        }
        
        
        self._var_units = {
            'water_surface__elevation': 'm',
            'land_surface__elevation': 'm',
            'manning_n_parameter': '-',
            'land_surface__initial_elevation': 'm',
        }
        
        self._grids = {
            0: ['water_surface__elevation'],
            1: ['land_surface__elevation'],
            2: ['manning_n_parameter'],
            3: ['land_surface__initial_elevation'],
        }
        
        self._grid_type = {
            0: 'unstructured_grid',
            1: 'unstructured_grid',
            2: 'unstructured_grid',
            3: 'unstructured_grid',
        }





    def update(self):
        """Advance model by one time step."""
        self._anuga.update()
        self._time += self.get_time_step()
        self._anuga._time = self._time

    def update_frac(self, time_frac):
        """Update model by a fraction of a time step.

        Parameters
        ----------
        time_frac : float
            Fraction fo a time step.
        """
        time_step = self.get_time_step()
        self._anuga.time_step = time_frac * time_step
        self.update()
        self._anuga.time_step = time_step

    def update_until(self, then):
        """Update model until a particular time.

        Parameters
        ----------
        then : float
            Time to run model until.
        """
        n_steps = (then - self.get_current_time()) / self.get_time_step()

        for _ in range(int(n_steps)):
            self.update()
        self.update_frac(n_steps - int(n_steps))

    def finalize(self):
        """Finalize model."""
        self._anuga = None
        
        
        
    """
    Var
    """
        

    def get_var_type(self, var_name):
        """Data type of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        str
            Data type.
        """
        return str(self.get_value_ref(var_name).dtype)

    def get_var_units(self, var_name):
        """Get units of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        str
            Variable units.
        """
        return self._var_units[var_name]

    def get_var_nbytes(self, var_name):
        """Get units of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        int
            Size of data array in bytes.
        """
        return self.get_value_ref(var_name).nbytes

    def get_var_grid(self, var_name):
        """Grid id for a variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        int
            Grid id.
        """
        for grid_id, var_name_list in self._grids.items():
            if var_name in var_name_list:
                return grid_id

    """
    Grids
    """

    def get_grid_rank(self, grid_id):
        """Rank of grid.

        Parameters
        ----------
        grid_id : int
            Identifier of a grid.

        Returns
        -------
        int
            Rank of grid.
        """
        return len(self.get_grid_shape(grid_id))

    def get_grid_size(self, grid_id):
        """Size of grid.

        Parameters
        ----------
        grid_id : int
            Identifier of a grid.

        Returns
        -------
        int
            Size of grid.
        """
        return np.prod(self.get_grid_shape(grid_id))
        
        
        
    """
    Values
    """

    def get_value_ref(self, var_name):
        """Reference to values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        array_like
            Value array.
        """
        return self._values[var_name]

    def get_value(self, var_name):
        """Copy of values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        array_like
            Copy of values.
        """
        return self.get_value_ref(var_name).copy()

    def get_value_at_indices(self, var_name, indices):
        """Get values at particular indices.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        indices : array_like
            Array of indices.

        Returns
        -------
        array_like
            Values at indices.
        """
        return self.get_value_ref(var_name).take(indices)

    def set_value(self, var_name, src):
        """Set model values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        src : array_like
            Array of new values.
        """
        val = self.get_value_ref(var_name)
        val[:] = src

    def set_value_at_indices(self, var_name, src, indices):
        """Set model values at particular indices.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        src : array_like
            Array of new values.
        indices : array_like
            Array of indices.
        """
        val = self.get_value_ref(var_name)
        val.flat[indices] = src



    def get_component_name(self):
        """Name of the component."""
        return self._name

    def get_input_var_names(self):
        """Get names of input variables."""
        return self._input_var_names

    def get_output_var_names(self):
        """Get names of output variables."""
        return self._output_var_names
      
      
        
    """
    Grid
    """
        
    def get_grid_x(self, grid_id = None):
        """Get coordinates of grid nodes in the streamwise direction"""
        return self._anuga.grid_x
        
    def get_grid_y(self, grid_id = None):
        """Get coordinates of grid nodes in the streamwise direction"""
        return self._anuga.grid_y
        
    def get_grid_z(self, grid_id = None):
        """Get elevation of the grid nodes"""
        return self._anuga.grid_z

    def get_grid_shape(self, grid_id):
        """Number of rows and columns of uniform rectilinear grid."""
        var_name = self._grids[grid_id][0]
        return self.get_value_ref(var_name).shape

    def get_grid_spacing(self, grid_id):
        """Spacing of rows and columns of uniform rectilinear grid."""
        pass

    def get_grid_origin(self, grid_id):
        """Origin of uniform rectilinear grid."""
        return (0., 0.)

    def get_grid_type(self, grid_id):
        """Type of grid."""
        return self._grid_type[grid_id]
        
        
    """
    Time
    """

    def get_start_time(self):
        """Start time of model."""
        return 0.

    def get_end_time(self):
        """End time of model."""
        return np.finfo('d').max

    def get_current_time(self):
        """Current time of model."""
        return self._time

    def get_time_step(self):
        """Time step of model."""
        return self._anuga.time_step
