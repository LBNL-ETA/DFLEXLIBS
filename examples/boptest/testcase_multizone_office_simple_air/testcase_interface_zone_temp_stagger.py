# Only allow 2 HVAC units to operate at a given time. 
# Widen the deadband of all other units 
# Based on Delta T (primarily) between setpoint and time since unit has been activated, prioritize unit. 
# Do not overwrite 
# %%
#from typing_extensions import Protocol
import sys
sys.path.insert(1, '../../../python')

from typing import Protocol
import rdflib
from collections import OrderedDict
from dflexlibs.hvac.functions import get_active_units, TSetHeaZon_TSetCooZon_stagger, get_delta_t
from dflexlibs.hvac.strategies.stra_stagger import (
    compute_control
)


# Class uses functions defined in the 'functions' module
class StaggerFunctions(Protocol):
    '''Contains the set of control functions needed for a Control Strategy.
    May differ by control strategy and interface. 
    Functions are pulled from controls.hvac.sequences.functions'''
        
    def get_active_units(self):
        ...
    def get_setpoints(self):
        ...

class BOPTestStaggerFunctions(StaggerFunctions):
    
    def __init__(self) -> None:
        self.get_active_units = get_active_units
        self.get_setpoints = TSetHeaZon_TSetCooZon_stagger
        self.get_delta_t = get_delta_t


class StaggerStrategy(Protocol):
    '''Class for a particular control strategy.
    control_functions is an instantiated object of type DRControlFunctions.
    compute_control will be pulled from library controls.hvac.sequences.strategies.
    A object of type ControlStrategy may be used by many different DRInterfaces.'''

    control_functions: StaggerFunctions
    
    def __init__(self, control_functions: StaggerFunctions):
        ...
    def main(self):
        ...
    def sparql_query(self):
        ...

class StaggerInterface():
    
    # Can optionally use a config file for the things in __init__ or just pass inputs as parameters to class
    def __init__(self):

        '''Interface for BOPTest to run stagger
        '''   
        config = {}
        self.TSetMin_baseline_schedule = config.get('TSetMin_baseline_schedule',
            [16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16])
        self.TSetMax_baseline_schedule = config.get('TSetMax_baseline_schedule',
            [21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21])
        # converting to K
        self.TSetMax_baseline_schedule = [ x + 273.15 for x in self.TSetMax_baseline_schedule]
        self.TSetMin_baseline_schedule = [ x + 273.15 for x in self.TSetMin_baseline_schedule]
        # Define temperature limit values
        self.Tlimit_min = config.get('Tlimit_min', 285.15) 
        self.Tlimit_max = config.get('Tlimit_max', 313.15) 
        self.active_unit_count = config.get('active_unit_count', 2)
        self.control_functions = BOPTestStaggerFunctions()
        self.compute_control = compute_control
        self.sparql_query = query_model
        self.sparql_results = {}
        # keys = 'range_query', 'TZonPoint', 'TSetZonPoint', 'TSetHeaZonPoint', 'TSetCooZonPoint'
        self.sparql_results = self.sparql_query(config.get('graph_path', 'test-model.ttl'))
        # self.sparql_results = { keys[i] : v for i,v in enumerate(results)}

    
    def control_agent(self, step, unit_dict, start_time_days = None):
    
        control_results = {}
        
        setpoints = self.compute_control(step, unit_dict, self.control_functions.get_active_units, 
                        self.control_functions.get_setpoints, self.control_functions.get_delta_t,
                        self.active_unit_count, 
                        self.Tlimit_min, self.Tlimit_max)                    
        
        control_results = setpoints

        print(control_results) 
        return control_results    

# %%
import rdflib
def query_model(filepath):
    """
    runs queries for multiple possible configurations of the model
    if both possible configurations work it'll choose deadband widening 
    it will also let the user know which queries passed. 
    """
    g = rdflib.Graph()
    g.parse(filepath, format = 'ttl')

    queries = {}

    queries['heating_and_cooling_setpoint'] = """
    SELECT DISTINCT *
    WHERE {
        ?zone a s223:DomainSpace ;
            s223:hasProperty ?TZon, ?TsetZonHeat, ?TsetZonCool .

        ?TsetZonCool a app:Heating_Setpoint ;
            ref:hasExternalReference/bacnet:object-name ?TsetZonHeatPoint  .

        ?TsetZonHeat a app:Cooling_Setpoint ;
            ref:hasExternalReference/bacnet:object-name ?TsetZonCoolPoint  .

        ?TZon a app:Zone_Temperature ;
            ref:hasExternalReference/bacnet:object-name  ?TZonPoint  .
        
    }"""

    queries['setpoint_and_mode'] = """
    SELECT DISTINCT *
    WHERE {
        ?zone a s223:DomainSpace ;
            s223:hasProperty ?TZon, ?TsetZon, ?Mode .

        ?TZon a app:Single_Temperature_Setpoint ;
        ref:hasExternalReference/bacnet:object-name ?TsetZonPoint  .

        ?TZon a app:Cooling_Setpoint ;
        ref:hasExternalReference/bacnet:object-name ?TsetZonCoolPoint  .

        ?TsetZon a app:Zone_Temperature ;
        ref:hasExternalReference/bacnet:object-name  ?TZonPoint  .
        
    }"""

    results_dict = {}
    for k, query in queries.items():
        results = g.query(query)
        # only if results have rows add them to the results_dict
        if results:
            results_dict[k] = sparql_to_dict(results)

    return results_dict

def sparql_to_dict(results, key = 'zone'):
    """
    turns results into a dictionary of dictionaries. the key for the containing dictionary can be selected
    turning everything to strings cause it may be easier
    """
    result_dict = {}
    
    for row in results:
        var_names = [var for var in results.vars]
        # Create a dictionary with variable names as keys and corresponding values
        values_dict = {str(var): str(row[var]) for var in var_names[1:]}
        
        result_dict[str(row[key])] = values_dict

    return result_dict

# %%
#Testing 
res_dict = query_model('test-model.ttl')

app = StaggerInterface()

data = {
    'unit_id1': {'TSetCooZon': 25,'TSetHeaZon': 22,'TSetZon': None, 'TZon': 20, 'active_step': 900},
    'unit_id2': {'TSetCooZon': 25,'TSetHeaZon': 22,'TSetZon': None, 'TZon': 31, 'active_step': 900},
    'unit_id3': {'TSetCooZon': 25,'TSetHeaZon': 22,'TSetZon': None, 'TZon': 28, 'active_step': 900},
    'unit_id4': {'TSetCooZon': 25,'TSetHeaZon': 22,'TSetZon': None, 'TZon': 23, 'active_step': 900},
    'unit_id5': {'TSetCooZon': 25,'TSetHeaZon': 22,'TSetZon': None, 'TZon': 25, 'active_step': 900},
}

app.control_agent(900, data)
# %%
