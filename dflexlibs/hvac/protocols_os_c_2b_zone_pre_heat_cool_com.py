#from typing_extensions import Protocol
from typing import Protocol

# Class uses functions defined in the 'functions' module
class DRControlFunctions(Protocol):
    '''Contains the set of control functions needed for a Control Strategy.
    May differ by control strategy and interface. 
    Functions are pulled from controls.hvac.sequences.functions'''
        
    def shift_price_occ_event(self):
        ... 
    def zone_qualification_check(self):
        ...
    def shift_check_modulation(self):
        ...   
    def shift_single_step_adjs_zone(self):
        ...
    def shift_target_demand_mod(self):
        ...      
    
# compute control will probably come from the 'strategies' module
class DRControlStrategy(Protocol):
    '''Class for a particular control strategy.
    control_functions is an instantiated object of type DRControlFunctions.
    compute_control will be pulled from library controls.hvac.sequences.strategies.
    A object of type ControlStrategy may be used by many different DRInterfaces.'''

    control_functions: DRControlFunctions
    
    def __init__(self, control_functions: DRControlFunctions):
        ...
    def compute_control(self):
        ...
    def sparql_query(self):
        ...
        
class DRInterface(Protocol):
    '''Class for different interfaces with DR control strategies.
    This interface transforms data to utilize a common control strategy. 
    Each platform will need its own interfaces.'''

    controls: DRControlStrategy

    def __init__(self,  controls: DRControlStrategy):
        ...
    def control_agent(self, y: dict, f: dict, step: int, start_time_days: int):
        ...
    def get_hvac_signal(self):
        ...
    def get_price_threshold(self):
        ...