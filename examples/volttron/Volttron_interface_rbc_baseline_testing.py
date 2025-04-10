import yaml
import sys
sys.path.append("..")
import os
import pandas as pd

from dflexlibs.hvac.strategies.stra_rbc_baseline_testing import (
    compute_control,
    sparql_query
)
from dflexlibs.hvac.protocols_rbc_baseline_testing import (
    DRControlFunctions,
    DRControlStrategy,
    DRInterface
)

class VolttronControlFunctions(DRControlFunctions):
    
    def __init__(self):
        ...
        
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

        self.occ_cmd_encoding = config.get('occ_cmd_encoding', None)
        self.non_occ_cmd_encoding = config.get('non_occ_cmd_encoding', None)  

        self.sparql_results = sparql_query(self.graph_path, self.query_paths)
        self.compute_control = controls.compute_control
        self.control_functions = controls.control_functions

        
    def control_agent(self, step, current_time, operation_mode, y, prev_output):
        
        control_results = {}
        occ_cmd_results = {}
        baseline_values = {}

        print(current_time)
        print(y)
        
        # Read baseline setpoint values        
        baseline_df = pd.read_csv(self.baseline_path) 

        def get_value(df, time, point):
            time = int(time)
            row = df[(df["Time"] == time)]
            
            if not row.empty:
                return row[point].values[0]
            return None
            
        def get_schedule (step, df, current_time, current_value, point):
            schedule = []
            num_steps = int(24 / step)
            for i in range(num_steps):  
                offset = step * i # list with values every hour
                next_time = current_time + offset
                if next_time >= 24:
                    next_time -= 24
                next_value = get_value(df, next_time, point)
                if next_value is not None:
                    current_value = next_value
                schedule.append(float(current_value))
            return schedule

        # Initiliaze values from the SPARQL query module
        number_of_zones = zone_names = zone_set_temp_point = zone_set_temp_heat_point = zone_set_temp_cool_point = unocc_zone_set_temp_heat_point = unocc_zone_set_temp_cool_point = occ_zone_set_temp_heat_point = occ_zone_set_temp_cool_point = occ_sensor_point = occ_cmd_point = None        
        number_of_zones, zone_names, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, unocc_zone_set_temp_heat_point, unocc_zone_set_temp_cool_point, occ_zone_set_temp_heat_point, occ_zone_set_temp_cool_point, occ_sensor_point, occ_cmd_point = self.sparql_results

        print(number_of_zones, zone_names, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, unocc_zone_set_temp_heat_point, unocc_zone_set_temp_cool_point, occ_zone_set_temp_heat_point, occ_zone_set_temp_cool_point, occ_sensor_point, occ_cmd_point)

        print(operation_mode) #'heat' or 'cool'    


        if number_of_zones != None:
            # Iterate over each zone
            for zone in number_of_zones:  
                # Get zone name
                zone_name = ' '.join([zone_names[zone]])
                print(zone_name)

                current_occ_value = get_value(baseline_df, current_time, occ_sensor_point[zone])

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
                    zone_set_temp_heat_bas_schedule = get_schedule (step, baseline_df, current_time, current_baseline_value, zone_set_temp_heat_point[zone])
                    zone_set_temp_heat_bas_schedule = [int(x) for x in zone_set_temp_heat_bas_schedule]

                if zone_set_temp_cool_point is not None:
                    # Get current setpoint
                    zone_set_temp_cool = y[zone_set_temp_cool_point[zone]]
                    zone_set_temp_cool_name = ' '.join([zone_set_temp_cool_point[zone]])

                     # Get baseline setpoint schedule
                    current_baseline_value = get_value(baseline_df, current_time, zone_set_temp_cool_point[zone])
                    zone_set_temp_cool_bas_schedule = get_schedule (step, baseline_df, current_time, current_baseline_value, zone_set_temp_cool_point[zone])
                    zone_set_temp_cool_bas_schedule = [int(x) for x in zone_set_temp_cool_bas_schedule]
                
                print('TSetHeaZon', zone_set_temp_heat, 'TSetHeaZon_baseline', zone_set_temp_heat_bas_schedule)
                print('TSetCooZon', zone_set_temp_cool, 'TSetCooZon_baseline', zone_set_temp_cool_bas_schedule)


                # Call selected control strategy 
                results = (self.compute_control(
                    zone_set_temp_heat, zone_set_temp_cool, zone_set_temp_heat_name, zone_set_temp_cool_name,
                    zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule))
                
                control_results.update(results)  

                # if unoccupied
                if occ_cmd_point and current_occ_value == 0:
                    occ_cmd_results[' '.join([occ_cmd_point[zone]])] = self.non_occ_cmd_encoding
                    
                    # get baseline values for occ period as the unoccupied setpoints will be changed by the control
                    baseline_values[' '.join([occ_zone_set_temp_heat_point[zone]])] = get_value(baseline_df, current_time, occ_zone_set_temp_heat_point[zone])
                    baseline_values[' '.join([occ_zone_set_temp_cool_point[zone]])] = get_value(baseline_df, current_time, occ_zone_set_temp_cool_point[zone])

                # if occupied
                elif occ_cmd_point and current_occ_value == 1:
                    occ_cmd_results[' '.join([occ_cmd_point[zone]])] = self.occ_cmd_encoding

                    # get baseline values for unocc period as the occupied setpoints will be changed by the control
                    baseline_values[' '.join([unocc_zone_set_temp_heat_point[zone]])] = get_value(baseline_df, current_time, unocc_zone_set_temp_heat_point[zone])
                    baseline_values[' '.join([unocc_zone_set_temp_cool_point[zone]])] = get_value(baseline_df, current_time, unocc_zone_set_temp_cool_point[zone])

              
        control_results.update(occ_cmd_results)
        control_results.update(baseline_values)
        print(control_results)
        
        return control_results