import yaml
import sys
sys.path.append("..")
import os

from controls.hvac.sequences.python.strategies.stra_zone_temp_shift_shed_price import (
    compute_control,
    sparql_query
)
from controls.hvac.protocols_zone_temp import (
    DRControlFunctions,
    DRControlStrategy,
    DRInterface
)
from controls.hvac.sequences.python.functions import (
    
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

class BOPTestControlFunctions(DRControlFunctions):
    
    def __init__(self):
        self.setpoint_adjustment = ashrae_TSet_adjust
        self.new_comfort_range = new_comfort_range
        self.runaway_condition = runaway_condition
        self.heat_runaway = runaway_TsetHeaZon
        self.cool_runaway = runaway_TsetCooZon
        self.shed_price_event = shed_price_event
        self.heat_shed = shed_TsetHeaZon
        self.cool_shed = shed_TsetCooZon
        self.shift_occ_price_event = shift_occ_price_event
        self.heat_shift = shift_TsetHeaZon
        self.cool_shift = shift_TsetCooZon   

class BOPTestControls(DRControlStrategy):
    
    def __init__(self, control_functions: BOPTestControlFunctions):
        self.control_functions = control_functions
        self.compute_control = compute_control

class BOPTestInterface(DRInterface):
    
    # Can optionally use a config file for the things in __init__ or just pass inputs as parameters to class
    def __init__(self, controls, config_path):

        '''Interface for BOPTest to run DR Control Strategies
        '''   
        try:
            with open(config_path) as fp:
                config = yaml.safe_load(fp)
        except Exception as e:
            print('Error reading configuration file')
            print(e)
        
        # Define query and graph path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_path = os.path.join(current_dir, config["sparql_query"])

        self.graph_path = config.get('graph_path')         

        # Define price identifier and threshold
        self.price_identifier = config.get('price_identifier', 'PriceElectricPowerDynamic')
        self.price_threshold_value = config.get('price_threshold_value')

        # Define temperature limit values
        self.Tlimit_min = config.get('Tlimit_min') 
        self.Tlimit_max = config.get('Tlimit_max') 
        
        # Define identifier for defining HVAC operation mode  
        self.hvac_mode_identifier = config.get('hvac_mode_identifier', None) # for single control signal
        self.heat_signal_identifier = config.get('heat_signal_identifier', None) # for heating control signal
        self.cool_signal_identifier = config.get('cool_signal_identifier', None) # for cooling control signal
        
        # If setpoint from baseline control follows comfort range, comfort range needs adjustment to allow shed control
        self.adj_comfort_range_flag = config.get('adj_comfort_range_flag',True)
        self.adj_comfort_range_value = config.get('adj_comfort_range_value',2)
        
        # Initialize values for the get_hvac_signal function
        self.heat_signal = 0
        self.cool_signal = 0
        self.TSetHeaZonPoint = None
        self.TSetCooZonPoint = None

        self.shift_horizon_time = config.get('shift_horizon_time')

        self.sparql_results = sparql_query(self.graph_path, self.query_path)
        self.compute_control = controls.compute_control
        self.control_functions = controls.control_functions

    def get_hvac_signal(self):
        ...

    def iterate_lists(self):
        ...
    
    def get_occ_min(self):
        ...
    
    def get_price_threshold(self):
        ...
    
    def control_agent(self, y, f, step, start_time_days):
        '''Call compute_control function from the selected control strategy and functions based on measurement and forecast values.
    
        Parameters
        ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        f : dict
            Contains the current values of the forecasts.
            {:}

        step : int
            Contains the current step value.

        
        start_time_days : int
            Contains start time of the test period in days.

        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
        control_results = {}
        # Get energy price  
        price_schedule = f[self.price_identifier]                            
        price_threshold_value = self.get_price_threshold(price_schedule)
        print('price_threshold_value', price_threshold_value)

        # Initiliaze values from the SPARQL query module
        range_query = TZonPoint = TSetZonPoint = TSetHeaZonPoint = TSetCooZonPoint = TSetMinPoint = TSetMaxPoint = occSensorPoint = None
        range_query, TZonPoint, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, TSetMinPoint, TSetMaxPoint, occSensorPoint = self.sparql_results
        
        # Define HVAC heat_signal and cool_signal
        self.heat_signal, self.cool_signal, self.TSetHeaZonPoint, self.TSetCooZonPoint = self.get_hvac_signals(y, self.hvac_mode_identifier, self.heat_signal_identifier, 
                                                                   self.cool_signal_identifier, TSetZonPoint, TSetHeaZonPoint, 
                                                                   TSetCooZonPoint, self.heat_signal, self.cool_signal)
        
        print('self.cool_signal', self.cool_signal, 'self.heat_signal', self.heat_signal)        

        if range_query is not None:
            # Iterate over each zone
            for zone in range_query:  
                        
                # Get temperature heating and cooling setpoints per zone
                TSetHeaZon = TSetHeaZon_name = TSetCooZon = TSetCooZon_name = None
                if self.TSetHeaZonPoint is not None:
                    TSetHeaZon = y[self.TSetHeaZonPoint[zone]]                
                    TSetHeaZon_name = ' '.join([self.TSetHeaZonPoint[zone]])
                if self.TSetCooZonPoint is not None:
                    TSetCooZon = y[self.TSetCooZonPoint[zone]]
                    TSetCooZon_name = ' '.join([self.TSetCooZonPoint[zone]])
                
                print('TSetHeaZon', TSetHeaZon)
                print('TSetCooZon', TSetCooZon)

                # Get zone temperature
                TZon = y[TZonPoint[zone]]
                print('TZon', TZon)

                # Get comfort range according to occupancy schedule
                TSetMin_baseline_schedule = f[TSetMinPoint[zone]]
                TSetMax_baseline_schedule = f[TSetMaxPoint[zone]]

                # Get occupancy schedule and occupancy status/sensor value 
                # occupancy_schedule could easily use a "self.occ_schedule_identifier" from config file if there is only one schedule for all zones.
                # But to simplify the BOPTEST interface, here we are using same identifier for both occ schedule and status
                # coming from the BOPTEST forecast identifier added in the graph as the Brick class for occ sensor.
                # The constraints here are that BOPTEST has no occ sensor values, so the forecast is used,
                # and that brick has no class for schedule, so the code would be a bit more complex if one would iterate of 
                # a list of identifiers per zone defined in the config file 
                occupancy_schedule = f[occSensorPoint[zone]] 

                occ_min_threshold = self.get_occ_min(occupancy_schedule)
                print("occ_min_threshold", occ_min_threshold)
                
                occupancy_status = f[occSensorPoint[zone]]

                print("price_schedule", price_schedule)
                print("occupancy_schedule", occupancy_schedule)

                # Iterate lists from occupancy schedule, occupancy status and price
                # consider lists with 24 values, 1 per hour 
                current_TSetMin_baseline, current_TSetMax_baseline, current_occ_schedule, current_occ_status, current_price, future_price, future_occ_schedule , future_TSetMin_baseline, future_TSetMax_baseline= self.iterate_lists(
                    TSetMin_baseline_schedule, TSetMax_baseline_schedule, occupancy_schedule, occupancy_status, price_schedule, self.shift_horizon_time)

                print("current_occ_status", current_occ_status)
                print("current_occ_schedule", current_occ_schedule)
                print("future_occ_schedule", future_occ_schedule)
                print("current_price", current_price)
                print("future_price", future_price)
                    
                # Call selected control strategy 
                control_results.update(
                        self.compute_control(self.control_functions.setpoint_adjustment, self.control_functions.runaway_condition, 
                                            self.control_functions.heat_runaway, self.control_functions.cool_runaway, self.control_functions.shift_occ_price_event, 
                                            self.control_functions.shed_price_event, self.control_functions.heat_shift, 
                                            self.control_functions.cool_shift, self.control_functions.heat_shed, 
                                            self.control_functions.cool_shed, self.control_functions.new_comfort_range, 
                                            step, TZon, current_TSetMin_baseline, current_TSetMax_baseline, TSetHeaZon, TSetCooZon, 
                                            self.Tlimit_min, self.Tlimit_max, current_price, future_price, price_threshold_value, current_occ_status, current_occ_schedule, 
                                            future_occ_schedule, occ_min_threshold, self.adj_comfort_range_flag, self.adj_comfort_range_value, 
                                            self.heat_signal, self.cool_signal, TSetHeaZon_name, TSetCooZon_name, start_time_days, future_TSetMin_baseline, 
                                            future_TSetMax_baseline))
                    
                # Change dictionary key name from TSetXxxZon_name + 'enable' to TSetXxxZon_name[:-1] + activate
                if self.TSetHeaZonPoint is not None:
                    control_results = { k.replace(TSetHeaZon_name + '_enable', TSetHeaZon_name[:-1] + 'activate'): v for k, v in control_results.items() }
                if self.TSetCooZonPoint is not None:
                    control_results = { k.replace(TSetCooZon_name + '_enable', TSetCooZon_name[:-1] + 'activate'): v for k, v in control_results.items() }

        print(control_results) 
        return control_results