import yaml
import sys
sys.path.append("..")
import os
import pandas as pd

from dflexlibs.hvac.strategies.stra_os_c_1a2b_zone_temp_adj_inc_ratch_pre_heat_cool_com import (
    compute_control,
    sparql_query
)
from dflexlibs.hvac.protocols_os_c_1a2b_zone_temp_adj_inc_ratch_pre_heat_cool_com import (
    DRControlFunctions,
    DRControlStrategy,
    DRInterface
)
from dflexlibs.hvac.functions import (
    
    shed_price_event,
    shed_savings_mode,
    zone_qualification_check,
    shed_single_step_adj_zone,
    shed_incr_temp_ratch_zone, 
    rebound_management_zone,
    shift_price_occ_event,
    shift_check_demand,
    shift_single_step_adjs_zone,
    shift_target_demand_mod
)

class BOPTestControlFunctions(DRControlFunctions):
    
    def __init__(self):
        self.shed_price_event = shed_price_event
        self.shed_savings_mode = shed_savings_mode
        self.zone_qualification_check = zone_qualification_check
        self.shed_single_step_adj_zone = shed_single_step_adj_zone
        self.shed_incr_temp_ratch_zone = shed_incr_temp_ratch_zone
        self.rebound_management_zone = rebound_management_zone

        self.shift_price_occ_event = shift_price_occ_event
        self.shift_single_step_adjs_zone = shift_single_step_adjs_zone
        self.shift_check_demand = shift_check_demand
        self.shift_target_demand_mod = shift_target_demand_mod

        

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
        self.query_paths = [os.path.join(current_dir, path) for path in config["sparql_query"]]
        self.graph_path = os.path.join(current_dir, config.get('graph_path'))

         # Define baseline path
        self.baseline_path = os.path.join(current_dir, config.get('baseline_path'))     

        # Define price identifier and threshold
        self.price_identifier = config.get('price_identifier', None)

        # Define identifier for defining HVAC operation mode  
        self.hvac_mode_identifier = config.get('hvac_mode_identifier', None) # for single control signal
        self.heat_signal_identifier = config.get('heat_signal_identifier', None) # for heating control signal
        self.cool_signal_identifier = config.get('cool_signal_identifier', None) # for cooling control signal
        
        # Define values for min and max temperature setpoints during shed/shift
        self.occ_flex_set_temp_min = config.get('occ_flex_set_temp_min') + 273  
        self.occ_flex_set_temp_max = config.get('occ_flex_set_temp_max') + 273  
        self.non_occ_flex_set_temp_min = config.get('non_occ_flex_set_temp_min') + 273  
        self.non_occ_flex_set_temp_max = config.get('non_occ_flex_set_temp_max') + 273 

        # Define adjustment factor for the temperature setpoint during first shed
        self.shed_initial_adjust = config.get('shed_initial_adjust', None)

        # Define values for ratcheting
        self.shed_dev_threshold = config.get('shed_dev_threshold', None)
        self.shed_delta_ratchet = config.get('shed_delta_ratchet', None)

        # Define shift values
        self.shift_adjust = config.get('shift_adjust', None)
        self.shift_dev_threshold = config.get('shift_dev_threshold', None)
        self.shift_horizon_time = config.get('shift_horizon_time', None)

        self.peak_demand_diff_error_min = config.get('peak_demand_diff_error_min', None)
        self.deadband_peak_demand_diff_error_min = config.get('deadband_peak_demand_diff_error_min', None)

        # Define name of handsoff zones
        self.hands_off_zone = config.get('hands_off_zone', None)

        self.shed_counter_dict = {}
        self.shift_counter_dict = {}
        self.reduce_VAV = 0

        self.sparql_results = sparql_query(self.graph_path, self.query_paths)
        self.compute_control = controls.compute_control
        self.control_functions = controls.control_functions


    def get_hvac_signal(self):
        ...
    
    def get_price_threshold(self):
        ...
    
    def control_agent(self, y, f, step, start_time_days, current_time, f_price):
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

        
        current_time : int
            Contains current time in seconds.

        
        f_price :  dict
            Contains the values of price forecast for a 2-week period.
            {:}

        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
        control_results = {}
        print(current_time, step)
        print(self.shed_counter_dict)
        print(self.shift_counter_dict)

        shift_horizon_time = int(self.shift_horizon_time * (3600 / step))
      
        # Read baseline setpoint values        
        baseline_df = pd.read_csv(self.baseline_path) 

        def get_baseline_value(baseline_df, current_time, point, offset=0):
            filtered_df = baseline_df[baseline_df['time'] == current_time + offset]
            pos = -1 if len(filtered_df) > 1 else 0 #gets last value if there is more than one value for the current time
            return filtered_df.iloc[pos][point] if not filtered_df.empty else None  
                    
        def calculate_baseline(baseline_df, current_time, zone):
            current_value = get_baseline_value(baseline_df, current_time, zone)
            previous_value = get_baseline_value(baseline_df, current_time, zone, -30)
            next_value = get_baseline_value(baseline_df, current_time, zone, 90)

            if previous_value is not None and next_value is not None and previous_value == current_value:
                return next_value
            return current_value

        ratcheting_list = {}
        rebound_heat_list = {}
        rebound_cool_list = {}
        ratcheting_list_unshift = {}

        # Get energy price  
        schedule_price = f[self.price_identifier]                            
        price_threshold_value = self.get_price_threshold(f_price[self.price_identifier])
        print('price_threshold_value', price_threshold_value)

        # Initiliaze values from the SPARQL query module
        number_of_zones = zone_names = zone_temp_point = zone_set_temp_point = zone_set_temp_heat_point = zone_set_temp_cool_point = set_temp_min_point = set_temp_max_point = occ_sensor_point = vav_damper_set_point = vav_discharge_temp_point = vav_reheat_command_point = ahu_supply_temp_point = ahu_supply_flow_point = ahu_supply_flow_set_point = ele_pow_point = therm_pow_point = None
        number_of_zones, zone_names, zone_temp_point, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, set_temp_min_point, set_temp_max_point, occ_sensor_point, vav_damper_set_point, vav_discharge_temp_point, vav_reheat_command_point, ahu_supply_temp_point, ahu_supply_flow_point, ahu_supply_flow_set_point, ele_pow_point, therm_pow_point = self.sparql_results
        print(number_of_zones, zone_names, zone_temp_point, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, set_temp_min_point, set_temp_max_point, occ_sensor_point, vav_damper_set_point, vav_discharge_temp_point, vav_reheat_command_point, ahu_supply_temp_point, ahu_supply_flow_point, ahu_supply_flow_set_point, ele_pow_point, therm_pow_point)

        power_points = ele_pow_point + therm_pow_point
        print(power_points)
        
        #print(get_baseline_value(baseline_df, current_time, power_points))

        baseline_demand_df = pd.read_csv(self.baseline_path, parse_dates=['time'])

        # Convert the 'time' column to datetime
        baseline_demand_df['time'] = pd.to_datetime(baseline_demand_df['time'], unit='s')

        # Set the 'time' column as the index
        baseline_demand_df.set_index('time', inplace=True)

        baseline_demand_df['Total'] = baseline_demand_df[power_points].sum(axis=1)

        resampled_mean_total = baseline_demand_df['Total'].resample('15T').mean()

        baseline_demand_peak = resampled_mean_total.max()
        
        current_demand = 0
        for powSensorPointName in power_points:
            #print(powSensorPointName)
            if powSensorPointName in list(y):
                #print(y[powSensorPointName])
                current_demand += y[powSensorPointName]

        print("baseline_demand_peak", baseline_demand_peak, "current_demand", current_demand) 


        if not zone_set_temp_heat_point or all(x is None for x in zone_set_temp_heat_point):
            zone_set_temp_heat_point = zone_set_temp_point
            zone_set_temp_cool_point = None
        elif not zone_set_temp_cool_point or all(x is None for x in zone_set_temp_cool_point):
            zone_set_temp_heat_point = None
            zone_set_temp_cool_point = zone_set_temp_point
        else:
            # Retain the existing values as they are not None or empty
            zone_set_temp_heat_point = zone_set_temp_heat_point
            zone_set_temp_cool_point = zone_set_temp_cool_point

        operation_mode = self.get_hvac_signals(y, self.hvac_mode_identifier, self.heat_signal_identifier, self.cool_signal_identifier, start_time_days)

        print(operation_mode)        

        # Get AHU measurements            
        ahu_supply_temp = ahu_supply_flow = ahu_supply_flow_set = None

        if ahu_supply_temp_point != None: 
            ahu_supply_temp = y[ahu_supply_temp_point]

        if ahu_supply_flow_point != None: 
            ahu_supply_flow = y[ahu_supply_flow_point]

        if ahu_supply_flow_set_point != None: 
            ahu_supply_flow_set = y[ahu_supply_flow_set_point]    

        elif ahu_supply_flow_point != None:
            ahu_supply_flow_set = y[ahu_supply_flow_point] # for when BOPTEST test case has no supply airflow setpoint

        if number_of_zones != None:
            # Iterate over each zone
            for zone in number_of_zones:  
                # Get zone name
                zone_name = ' '.join([zone_names[zone]])
                
                # Get temperature heating and cooling setpoints per zone
                zone_set_temp_heat = zone_set_temp_heat_name = zone_set_temp_cool = zone_set_temp_cool_name = None

                zone_set_temp_heat_bas_schedule = []
                zone_set_temp_cool_bas_schedule = []

                if zone_set_temp_heat_point is not None:
                    # Get current setpoint
                    zone_set_temp_heat = y[zone_set_temp_heat_point[zone]]                
                    zone_set_temp_heat_name = ' '.join([zone_set_temp_heat_point[zone]])

                    # Get baseline setpoint schedule
    
                    baseline_value = calculate_baseline(baseline_df, current_time, zone_set_temp_heat_point[zone])
                    
                    for i in range(24*4):  
                        offset = (3600/4) * i # list with values every 15 min
                        next_baseline_value = calculate_baseline(baseline_df, current_time + offset, zone_set_temp_heat_point[zone])
                        if next_baseline_value is not None:
                            baseline_value = next_baseline_value

                        zone_set_temp_heat_bas_schedule.append(float(baseline_value))

                if zone_set_temp_cool_point is not None:
                    # Get current setpoint
                    zone_set_temp_cool = y[zone_set_temp_cool_point[zone]]
                    zone_set_temp_cool_name = ' '.join([zone_set_temp_cool_point[zone]])

                     # Get baseline setpoint schedule
                    
                    baseline_value = calculate_baseline(baseline_df, current_time, zone_set_temp_cool_point[zone])

                    for i in range(24*4):  
                        offset = (3600/4) * i # list with values every 15 min
                        next_baseline_value = calculate_baseline(baseline_df, current_time + offset, zone_set_temp_cool_point[zone])
    
                        if next_baseline_value is not None:
                            baseline_value = next_baseline_value
                        
                        zone_set_temp_cool_bas_schedule.append(float(baseline_value))
                
                print('TSetHeaZon', zone_set_temp_heat, 'TSetHeaZon_baseline', zone_set_temp_heat_bas_schedule)
                print('TSetCooZon', zone_set_temp_cool, 'TSetCooZon_baseline', zone_set_temp_cool_bas_schedule)

                # Get zone temperature
                zone_temp = y[zone_temp_point[zone]]
                print('TZon', zone_temp)

                # Get VAV measurements
                vav_damper_set = vav_discharge_temp = vav_reheat_command = None

                if vav_damper_set_point and zone < len(vav_damper_set_point) and vav_damper_set_point[zone]:
                    vav_damper_set = y[vav_damper_set_point[zone]]
                    
                if vav_discharge_temp_point and zone < len(vav_discharge_temp_point) and vav_discharge_temp_point[zone]:
                    vav_discharge_temp = y[vav_discharge_temp_point[zone]]

                if vav_reheat_command_point and zone < len(vav_reheat_command_point) and vav_reheat_command_point[zone]:
                    vav_reheat_command = y[vav_reheat_command_point[zone]]

                print(vav_damper_set, vav_discharge_temp, vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set)

                # Get occupied signal for the operation of the HVAC system
                # because in the baseline control of BOPTEST test cases often do not follow the occ forecast values
                # here we are using the TSetHeaZon schedule to derive the occ schedule     

                # To print occ schedule
                schedule_occupancy = [1 if ele > baseline_df[zone_set_temp_heat_point[zone]].min() else 0 for ele in zone_set_temp_heat_bas_schedule]
                print("occupancy_schedule", schedule_occupancy)
                occ_min_threshold = 0

                print("price_schedule", schedule_price)
                   
                # Call selected control strategy 
                shed_counter, shift_counter, ratchet_list, rebound_h_list, rebound_c_list, results, reduce_VAV, ratchet_list_unshift = (self.compute_control(
                    self.control_functions.shed_price_event, self.control_functions.shed_savings_mode, self.control_functions.zone_qualification_check, self.control_functions.shed_single_step_adj_zone,  
                    self.control_functions.shed_incr_temp_ratch_zone, self.control_functions.rebound_management_zone, zone_temp, 
                    zone_set_temp_heat, zone_set_temp_cool, price_threshold_value, self.occ_flex_set_temp_min, 
                    self.occ_flex_set_temp_max, self.non_occ_flex_set_temp_min, self.non_occ_flex_set_temp_max, operation_mode, 
                    zone_set_temp_heat_name, zone_set_temp_cool_name, self.shed_counter_dict, zone, self.shed_initial_adjust, 
                    self.shed_dev_threshold, self.shed_delta_ratchet, self.hands_off_zone, zone_name, vav_damper_set, vav_discharge_temp, 
                    vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set, schedule_price, schedule_occupancy, 
                    occ_min_threshold, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                    self.shift_counter_dict, self.control_functions.shift_price_occ_event, shift_horizon_time, self.control_functions.shift_single_step_adjs_zone,
                    self.control_functions.shift_check_demand, baseline_demand_peak, current_demand, self.peak_demand_diff_error_min, self.deadband_peak_demand_diff_error_min, 
                    self.reduce_VAV, self.control_functions.shift_target_demand_mod,
                    self.shift_adjust, self.shift_dev_threshold))
                
                control_results.update(results)  
                self.shed_counter_dict[zone] = shed_counter
                self.shift_counter_dict[zone] = shift_counter
                print("new shed counter", self.shed_counter_dict[zone])
                print("new shift counter", self.shift_counter_dict[zone])
                ratcheting_list.update(ratchet_list) 
                 
                ratcheting_list_unshift.update(ratchet_list_unshift) 

                rebound_heat_list.update(rebound_h_list)                  
                rebound_cool_list.update(rebound_c_list) 

        self.reduce_VAV = reduce_VAV

        print(control_results)

        # Adding enable keys "TSetXxxZon_name[:-1] + activate" to the control results
        enable_keys_to_add = [key for key in control_results]
        new_items = []  # List to hold the new key-value pairs
        for key in enable_keys_to_add:
            new_key = key[:-1] + 'activate'
            new_items.append((key, control_results[key]))  # Original key-value pair
            new_items.append((new_key, 1))    # New key-value pair
        
        # Reconstruct control_results using the new key-value pairs
        control_results.clear()
        control_results.update(new_items)

        # Sort lists of zones    
        sorted_ratchet_zones = sorted(ratcheting_list, key=ratcheting_list.get, reverse=True)
        print("ratchet", sorted_ratchet_zones)

        sorted_rebound_heat_zones = sorted(rebound_heat_list, key=rebound_heat_list.get, reverse=True)
        print("rebound", sorted_rebound_heat_zones)

        sorted_rebound_cool_zones = sorted(rebound_cool_list, key=rebound_cool_list.get, reverse=True)
        print("rebound", sorted_rebound_cool_zones)

        sorted_ratchet_zones_unshift = sorted(ratcheting_list_unshift, key=ratcheting_list_unshift.get, reverse=True)
        print("ratchet_unshift", sorted_ratchet_zones_unshift)


        # Create a list of zones to filter out
        ratchet_zones_to_exclude = sorted_ratchet_zones[:-1]
        print(ratchet_zones_to_exclude)
        
        rebound_heat_zones_to_exclude = sorted_rebound_heat_zones[:-1]
        print(rebound_heat_zones_to_exclude)

        rebound_cool_zones_to_exclude = sorted_rebound_cool_zones[:-1]
        print(rebound_cool_zones_to_exclude)

        ratchet_zones_to_exclude_unshift = sorted_ratchet_zones_unshift[:-1]
        print(ratchet_zones_to_exclude_unshift)


        # Filter keys from control_results using keys_to_exclude
        filtered_control_results = {key: control_results[key] for key in control_results if not any(exclude_zone in key for exclude_zone in (ratchet_zones_to_exclude or rebound_heat_zones_to_exclude or rebound_cool_zones_to_exclude or ratchet_zones_to_exclude_unshift))}

        print(filtered_control_results)
        return filtered_control_results