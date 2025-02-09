import yaml
import sys
sys.path.append("..")
import os
import pandas as pd

from dflexlibs.hvac.strategies.stra_os_c_1a_zone_temp_adj_inc_ratch import (
    compute_control,
    sparql_query
)
from dflexlibs.hvac.protocols_os_c_1a_zone_temp_adj_inc_ratch import (
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
    rebound_management_zone
)

class VolttronControlFunctions(DRControlFunctions):
    
    def __init__(self):
        self.shed_price_event = shed_price_event
        self.shed_savings_mode = shed_savings_mode
        self.zone_qualification_check = zone_qualification_check
        self.shed_single_step_adj_zone = shed_single_step_adj_zone
        self.shed_incr_temp_ratch_zone = shed_incr_temp_ratch_zone
        self.rebound_management_zone = rebound_management_zone
        

class VolttronControls(DRControlStrategy):
    
    def __init__(self, control_functions: VolttronControlFunctions):
        self.control_functions = control_functions
        self.compute_control = compute_control

class VolttronInterface(DRInterface):

    def __init__(self, controls, config_path):

        '''Interface for Volttron to run DR Control Strategies
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
        
        # Define values for min and max temperature setpoints during shed
        self.occ_flex_set_temp_min = config.get('occ_flex_set_temp_min') #+ 273  
        self.occ_flex_set_temp_max = config.get('occ_flex_set_temp_max') #+ 273  
        self.non_occ_flex_set_temp_min = config.get('non_occ_flex_set_temp_min') #+ 273  
        self.non_occ_flex_set_temp_max = config.get('non_occ_flex_set_temp_max') #+ 273 

        # Define adjustment factor for the temperature setpoint during first shed
        self.shed_initial_adjust = config.get('shed_initial_adjust', None)

        # Define values for ratcheting
        self.shed_dev_threshold = config.get('shed_dev_threshold', None)
        self.shed_delta_ratchet = config.get('shed_delta_ratchet', None)

        # Define name of handsoff zones
        self.hands_off_zone = config.get('hands_off_zone', None)

        self.shed_counter_dict = {}

        self.sparql_results = sparql_query(self.graph_path, self.query_paths)
        self.compute_control = controls.compute_control
        self.control_functions = controls.control_functions

        self.degree_unit = config.get('degree_unit', None)

    def get_price_threshold(self):
        ...
    
    def control_agent(self, step, current_time, operation_mode, y):
        '''Call compute_control function from the selected control strategy and functions based on measurement and forecast values.
    
        Parameters
        ----------

        
        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
        control_results = {}
        print(current_time)
        print(y)
        print(self.shed_counter_dict)

        # Read baseline setpoint values        
        baseline_df = pd.read_csv(self.baseline_path) 

        def get_value(df, time, point):
            time = int(time)
            
            row = df[df["Time"] == time]
            if not row.empty:
                return row[point].values[0]
            return None
            
        def get_schedule (step, current_time, current_value, point):
            schedule = []
            num_steps = int(24 / step)
            for i in range(num_steps):  
                offset = step * i # list with values every hour
                next_time = current_time + offset
                if next_time >= 24:
                    next_time -= 24
                next_value = get_value(baseline_df, next_time, point)
                if next_value is not None:
                    current_value = next_value
                schedule.append(float(current_value))
            return schedule

        ratcheting_list = {}
        rebound_heat_list = {}
        rebound_cool_list = {}
        occ_cmd_results = {}

        # Get energy price schedule
        schedule_price = []
        current_price_value = get_value(baseline_df, current_time, self.price_identifier)
        schedule_price = get_schedule (step, current_time, current_price_value, self.price_identifier)

        price_threshold_value = self.get_price_threshold(baseline_df[self.price_identifier].tolist())
        print('price_threshold_value', price_threshold_value)

        # Initiliaze values from the SPARQL query module
        number_of_zones = zone_names = zone_temp_point = zone_set_temp_point = zone_set_temp_heat_point = zone_set_temp_cool_point = unocc_zone_set_temp_heat_point = unocc_zone_set_temp_cool_point = occ_zone_set_temp_heat_point = occ_zone_set_temp_cool_point = set_temp_min_point = set_temp_max_point = occ_sensor_point = occ_cmd_point = vav_damper_set_point = vav_discharge_temp_point = vav_reheat_command_point = ahu_supply_temp_point = ahu_supply_flow_point = ahu_supply_flow_set_point = None        
        number_of_zones, zone_names, zone_temp_point, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, unocc_zone_set_temp_heat_point, unocc_zone_set_temp_cool_point, occ_zone_set_temp_heat_point, occ_zone_set_temp_cool_point, set_temp_min_point, set_temp_max_point, occ_sensor_point, occ_cmd_point, vav_damper_set_point, vav_discharge_temp_point, vav_reheat_command_point, ahu_supply_temp_point, ahu_supply_flow_point, ahu_supply_flow_set_point = self.sparql_results

        print(number_of_zones, zone_names, zone_temp_point, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, unocc_zone_set_temp_heat_point, unocc_zone_set_temp_cool_point, occ_zone_set_temp_heat_point, occ_zone_set_temp_cool_point, set_temp_min_point, set_temp_max_point, occ_sensor_point, occ_cmd_point, vav_damper_set_point, vav_discharge_temp_point, vav_reheat_command_point, ahu_supply_temp_point, ahu_supply_flow_point, ahu_supply_flow_set_point)

        print(operation_mode) #'heat' or 'cool'    

        # Get AHU measurements            
        ahu_supply_temp = ahu_supply_flow = ahu_supply_flow_set = None

        if number_of_zones != None:
            # Iterate over each zone
            for zone in number_of_zones:  
                # Get zone name
                zone_name = ' '.join([zone_names[zone]])
                print(zone_name)

                # Get occ schedule
                current_occ_value = get_value(baseline_df, current_time, occ_sensor_point[zone])
                schedule_occupancy = get_schedule (step, current_time, current_occ_value, occ_sensor_point[zone])
                print("occupancy_schedule", schedule_occupancy)
                occ_min_threshold = 0

                print("price_schedule", schedule_price)
                
                #check if only zone_set_temp_point is available
                if (zone_set_temp_point) and operation_mode == 'heat':
                    zone_set_temp_heat_point = zone_set_temp_point
                    zone_set_temp_cool_point = None
                elif (zone_set_temp_point) and operation_mode == 'cool':
                    zone_set_temp_heat_point = None
                    zone_set_temp_cool_point = zone_set_temp_point
                #check if occ and unocc points are available
                elif current_occ_value == 1 and (occ_zone_set_temp_heat_point) and (occ_zone_set_temp_cool_point):
                    zone_set_temp_heat_point = occ_zone_set_temp_heat_point
                    zone_set_temp_cool_point = occ_zone_set_temp_cool_point
                elif current_occ_value == 0 and (occ_zone_set_temp_heat_point) and (occ_zone_set_temp_cool_point):
                    zone_set_temp_heat_point = unocc_zone_set_temp_heat_point
                    zone_set_temp_cool_point = unocc_zone_set_temp_cool_point
                else:
                    # Retain the existing values as they are not None or empty
                    zone_set_temp_heat_point = zone_set_temp_heat_point
                    zone_set_temp_cool_point = zone_set_temp_cool_point
                
                print(zone_set_temp_heat_point)
                print(zone_set_temp_cool_point)
                # Get temperature heating and cooling setpoints per zone
                zone_set_temp_heat = zone_set_temp_heat_name = zone_set_temp_cool = zone_set_temp_cool_name = None

                zone_set_temp_heat_bas_schedule = []
                zone_set_temp_cool_bas_schedule = []

                if zone_set_temp_heat_point is not None:
                    # Get current setpoint
                    zone_set_temp_heat = y[zone_set_temp_heat_point[zone]]  
                    zone_set_temp_heat_name = ' '.join([zone_set_temp_heat_point[zone]])

                    # Get baseline setpoint schedule    
                    current_baseline_value = get_value(baseline_df, current_time, zone_set_temp_heat_point[zone])
                    zone_set_temp_heat_bas_schedule = get_schedule (step, current_time, current_baseline_value, zone_set_temp_heat_point[zone])


                if zone_set_temp_cool_point is not None:
                    # Get current setpoint
                    zone_set_temp_cool = y[zone_set_temp_cool_point[zone]]
                    zone_set_temp_cool_name = ' '.join([zone_set_temp_cool_point[zone]])

                     # Get baseline setpoint schedule
                    current_baseline_value = get_value(baseline_df, current_time, zone_set_temp_cool_point[zone])
                    zone_set_temp_cool_bas_schedule = get_schedule (step, current_time, current_baseline_value, zone_set_temp_cool_point[zone])

                
                print('TSetHeaZon', zone_set_temp_heat, 'TSetHeaZon_baseline', zone_set_temp_heat_bas_schedule)
                print('TSetCooZon', zone_set_temp_cool, 'TSetCooZon_baseline', zone_set_temp_cool_bas_schedule)

                # Get zone temperature
                zone_temp = y[zone_temp_point[zone]]
                print('TZon', zone_temp)

                # Get VAV measurements
                vav_damper_set = vav_discharge_temp = vav_reheat_command = None

                # Call selected control strategy 
                shed_counter, ratchet_list, rebound_h_list, rebound_c_list, results = (self.compute_control(
                    self.control_functions.shed_price_event, self.control_functions.shed_savings_mode, self.control_functions.zone_qualification_check, self.control_functions.shed_single_step_adj_zone,  
                    self.control_functions.shed_incr_temp_ratch_zone, self.control_functions.rebound_management_zone, zone_temp, 
                    zone_set_temp_heat, zone_set_temp_cool, price_threshold_value, self.occ_flex_set_temp_min, 
                    self.occ_flex_set_temp_max, self.non_occ_flex_set_temp_min, self.non_occ_flex_set_temp_max, operation_mode, 
                    zone_set_temp_heat_name, zone_set_temp_cool_name, self.shed_counter_dict, zone, self.shed_initial_adjust, 
                    self.shed_dev_threshold, self.shed_delta_ratchet, self.hands_off_zone, zone_name, vav_damper_set, vav_discharge_temp, 
                    vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set, schedule_price, schedule_occupancy, 
                    occ_min_threshold, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule, self.degree_unit))
                
                if occ_cmd_point and current_occ_value == 0:
                    occ_cmd_results[' '.join([occ_cmd_point[zone]])] = 1
                elif occ_cmd_point and current_occ_value == 1:
                    occ_cmd_results[' '.join([occ_cmd_point[zone]])] = 2
                
                control_results.update(results)  
                self.shed_counter_dict[zone] = shed_counter
                print("new shed counter", self.shed_counter_dict[zone])
                ratcheting_list.update(ratchet_list)   
                rebound_heat_list.update(rebound_h_list)                  
                rebound_cool_list.update(rebound_c_list) 

        print(control_results)
        control_results.update(occ_cmd_results)
        print(control_results)

        # Sort lists of zones    
        sorted_ratchet_zones = sorted(ratcheting_list, key=ratcheting_list.get, reverse=True)
        print("ratchet", sorted_ratchet_zones)

        sorted_rebound_heat_zones = sorted(rebound_heat_list, key=rebound_heat_list.get, reverse=True)
        print("rebound", sorted_rebound_heat_zones)

        sorted_rebound_cool_zones = sorted(rebound_cool_list, key=rebound_cool_list.get, reverse=True)
        print("rebound", sorted_rebound_cool_zones)

        # Create a list of zones to filter out
        ratchet_zones_to_exclude = sorted_ratchet_zones[:-1]
        print(ratchet_zones_to_exclude)
        
        rebound_heat_zones_to_exclude = sorted_rebound_heat_zones[:-1]
        print(rebound_heat_zones_to_exclude)

        rebound_cool_zones_to_exclude = sorted_rebound_cool_zones[:-1]
        print(rebound_cool_zones_to_exclude)

        # Filter keys from control_results using keys_to_exclude
        filtered_control_results = {key: control_results[key] for key in control_results if not any(exclude_zone in key for exclude_zone in (ratchet_zones_to_exclude or rebound_heat_zones_to_exclude or rebound_cool_zones_to_exclude))}

        print(filtered_control_results)
        return filtered_control_results