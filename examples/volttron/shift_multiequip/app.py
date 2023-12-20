from typing import Protocol
import rdflib
from DFLEXLIBS.hvac.sequences.python.strategies.stra_zone_temp_shift_shed_price import (
    compute_control
)

from DFLEXLIBS.hvac.protocols_zone_temp import (
    DRControlFunctions,
    DRControlStrategy,
    DRInterface
)
from DFLEXLIBS.hvac.sequences.python.functions import (
    ashrae_TSet_adjust,
    new_comfort_range,
    runaway_condition,
    runaway_TsetHeaZon,
    runaway_TsetCooZon,
    shed_price_event,
    shed_TsetCooZon,
    shed_TsetHeaZon,
    shift_occ_price_event,
    shift_TsetCooZon,
    shift_TsetHeaZon
)

def null_runaway_condition(*args):
    '''Replacement for the runaway function if no runaway condition is used.
       Will return that there is no runaway condition.

        Parameters
        ----------            

        *args
            Accepts runaway condition inputs, though they are not used

        Returns
        -------

        False 

    '''    
    
    return False

def sparql_query(graph_path, query_path):

    '''Query identifiers for control points per zone from the selected graph path.

        Parameters
        ----------            

        graph_path : str
            Contains the path to the graph directory.
        
        query_path : str
            Contains the path to the sparql query.

        Returns
        -------

        range_query : int
            Contains the length of the query results, ie the number of zones with sufficient points from the graph. 

        TZonPoint : str
            Contains the identifier for the temperature measurement point per zone. 

        TSetZonPoint : str
            Contains the identifier for the temperature setpoint per zone.

        TSetHeaZonPoint : str
            Contains the identifier for the heating temperature setpoint per zone. 

        TSetCooZonPoint : str
            Contains the identifier for the cooling temperature setpoint per zone. 

    '''    

    # Query the identifiers for control points per zone    
    g = rdflib.Graph()
    g.parse(graph_path)
    with open(query_path) as f:
        query = f.read()
    qres = g.query(query)
    range_query = range(len(qres))

    # Create lists for the identifiers needed to instatiate the control points per zone
    TZonPoint = []
    TSetZonPoint = []
    TSetHeaZonPoint = []
    TSetCooZonPoint = []

    for row in qres:
        TZonPoint.append (str(row.TZonPoint))
        TSetZonPoint.append (str(row.TSetZonPoint))
        TSetHeaZonPoint.append (str(row.TSetHeaZonPoint))
        TSetCooZonPoint.append (str(row.TSetCooZonPoint))

    return range_query, TZonPoint, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint

class VolttronShiftControlFunctions(DRControlFunctions):
    '''
    The control functions needed to run the shift strategy from the Volttron platform
    Functions are same as those needed for BOPTest, however runaway conditions were not used
    '''
    
    def __init__(self):
        self.runaway_condition = null_runaway_condition
        self.heat_runaway = null_runaway_condition
        self.cool_runaway = null_runaway_condition
        self.shift_occ_price_event = shift_occ_price_event
        self.shed_price_event = shed_price_event
        self.heat_shed = shed_TsetHeaZon
        self.cool_shed = shed_TsetCooZon
        self.cool_shift = shift_TsetCooZon
        self.heat_shift = shift_TsetHeaZon
        self.setpoint_adjustment = ashrae_TSet_adjust
        self.new_comfort_range = new_comfort_range

class VolttronStrategy(DRControlStrategy):
    
    def __init__(self, control_functions):
        self.control_functions = control_functions
        self.compute_control = compute_control

class VolttronInterface(DRInterface):

    def __init__(self, controls, config):
        '''Interface compatible with Volttron Agent to run control app
        '''   
        self.heat_signal = config.get('heat_signal',0)
        self.cool_signal = config.get('cool_signal',0)
        self.price_schedule = config.get('price_schedule')
        self.occ_schedule = config.get('occ_schedule')
        self.price_threshold_value = config.get('price_threshold_value', 0.245)
        self.occ_min_threshold = config.get('occ_min_threshold', 1)
        self.adj_comfort_range_flag = config.get('adj_comfort_range_flag', False)
        self.adj_comfort_range_value = config.get('adj_comfort_range_value', 0)
        self.TSetMin_baseline_schedule = config.get('TSetMin_baseline_schedule',
            [16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16])
        self.TSetMax_baseline_schedule = config.get('TSetMax_baseline_schedule',
            [21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21])
        # Define temperature limit values
        self.Tlimit_min = config.get('Tlimit_min', 285.15) 
        self.Tlimit_max = config.get('Tlimit_max', 313.15) 
 
        self.user_setting = config.get('dr_control_setting', 'heat')

        self.compute_control = controls.compute_control
        self.control_functions = controls.control_functions
        self.sparql_query = sparql_query
        self.sparql_results = {}
        keys = 'range_query', 'TZonPoint', 'TSetZonPoint', 'TSetHeaZonPoint', 'TSetCooZonPoint'
        results = sparql_query(config.get('graph_path'), config.get('sparql_query_path'))
        self.sparql_results = { keys[i] : v for i,v in enumerate(results)}
        self.static_inputs = {
            'setpoint_adjustment' : self.control_functions.setpoint_adjustment,
            'runaway_condition' : self.control_functions.runaway_condition,
            'cool_runaway': self.control_functions.cool_runaway,
            'heat_runaway': self.control_functions.heat_runaway,
            'new_comfort_range' : self.control_functions.new_comfort_range, 
            'shift_occ_price_event' : self.control_functions.shift_occ_price_event,
            'shed_price_event' : self.control_functions.shed_price_event,
            'heat_shift' : self.control_functions.heat_shift,
            'cool_shift' : self.control_functions.cool_shift,
            'heat_shed' : self.control_functions.heat_shed,
            'cool_shed' : self.control_functions.cool_shed,
            'Tlimit_min' : self.Tlimit_min,
            'Tlimit_max' : self.Tlimit_max,
            'price_threshold_value' : self.price_threshold_value,
            'occ_min_threshold' : self.occ_min_threshold,
            'adj_comfort_range_flag' : self.adj_comfort_range_flag,
            'adj_comfort_range_value' : self.adj_comfort_range_value,
            'start_time_days': 0
        }

    def get_hvac_signal(self, user_setting = None):
        '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
        
        Parameters
        ----------

            user_setting (optional) : 'heat' or 'cool'
                Takes a user setting of either 'heat' or 'cool' to determine the signal

        Returns
        -------
            updated_heat_signal : int
                Contains heating signal to define the HVAC operation mode.

            updated_cool_signal : int
                Contains cooling signal to define the HVAC operation mode.
    '''
        
        if user_setting == 'heat':
            updated_cool_signal = 0
            updated_heat_signal = 1
        if user_setting == 'cool':
            updated_cool_signal = 1
            updated_heat_signal = 0
        
        return updated_cool_signal, updated_heat_signal
    
    def control_agent(self, TZon_lst, TSet_names, TSet_lst, step_lst, 
                      shift_lookahead, current_hour):
        '''Call compute_control function from the selected control strategy and functions based on measurement and forecast values.
    
        Parameters
        ----------
        TZon_lst : list
            list of zone temps
        TSet_lst : list
            list of zone(equip) setpoint values
        TSet_names : list
            list of names for each of the setpoints
        step_lst : list
            list of steps for each zone/equipment
        current_hour : int
            the current hour at the controlled site
        shift_look_ahead : int
            The amount of hours to lookahead to determine whether shifting should be used


        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
        control_results = []
        
        for i in range(0, len(TZon_lst)):

            cool_signal, heat_signal = self.get_hvac_signal(self.user_setting)
        
            print('cool_signal', cool_signal, 'heat_signal', heat_signal)        
                
            inputs =  {
                'step' : step_lst[i],
                'TZon' : TZon_lst[i],
                'TSetMin_baseline' : self.TSetMin_baseline_schedule[current_hour],
                'TSetMax_baseline' : self.TSetMax_baseline_schedule[current_hour],
                'future_TSetMin_baseline' : self.TSetMin_baseline_schedule[current_hour + shift_lookahead],
                'future_TSetMax_baseline' : self.TSetMax_baseline_schedule[current_hour + shift_lookahead],
                'TSetHeaZon' : TSet_lst[i],
                'TSetCooZon' : None,
                'heat_signal' : heat_signal,
                'cool_signal' : cool_signal,
                'TSetHeaZon_name' : TSet_names[i],
                'TSetCooZon_name' : TSet_names[i],
                'current_price' : self.price_schedule[current_hour],
                'future_price' : self.price_schedule[current_hour + shift_lookahead],
                'current_occ_status' : self.occ_schedule[current_hour],
                'current_occ_schedule' : self.occ_schedule[current_hour],
                'future_occ_schedule' : self.occ_schedule[current_hour + shift_lookahead],
                
                }
            
            inputs.update(self.static_inputs)
            control_row = self.compute_control(**inputs)
            control_results.append(control_row)


        Zon_temp_dict = {name:TZon_lst[i] for i, name in enumerate(TSet_names)}
        prioritized_units = self.add_demand_limiting_output(control_results, Zon_temp_dict)

        return control_results, prioritized_units
    

    def add_demand_limiting_output(self, control_results, Zon_temp_dict, amt_units = 2):
        """
        determines which units should be on based on the control results, 
        prioritizing a high difference between zone temps and zone setpts.

         Parameters
        ----------
        control_results : dict
            The control outputs to be used for the next step.
            {:}
        Zon_temp_dict : dict
            Dictionary of the current temperatures in each zone.
        amt_units : int
            The amount of HVAC units that should be on at a given time


        Returns
        -------
        prioritized_units : dict
            Defines which units should be prioritized based on zone temperatures
            {:}
        """
        temps = {}
        setpts = {}
        for dict in control_results:
            for k, v in dict.items():
                if ('enable' not in k):
                    setpts[k] = v
                    temps[k] = Zon_temp_dict[k]

        diffs = {k: v - temps[k] for k,v in setpts.items()}         
        sorted_diffs = sorted(diffs.items(), key=lambda item: item[1], reverse = True) 
        prioritized_units = [k + "_on" for k, v in sorted_diffs[:amt_units]]

        return prioritized_units
        

def create_application(config):
    '''
    Takes a configuration dictionary and returns an instantiated application with the volttron interface

    Parameters
        ----------
        config : dict
            A configuration dictionary needed for initializing VolttronInterface

        Returns
        -------
        app : VolttronInterface
            A fully initialized instance of VolttronInterface
        """
    '''
    functions = VolttronShiftControlFunctions()
    controls = VolttronStrategy(functions)
    app = VolttronInterface(controls, config)
    return app