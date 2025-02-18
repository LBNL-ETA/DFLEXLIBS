def compute_control(shed_price_event, shed_savings_mode, zone_qualification_check, shed_single_step_adj_zone, shed_perform_target_ratch,
                    rebound_management_zone, zone_temp, 
                    zone_set_temp_heat, zone_set_temp_cool, price_threshold_value, occ_flex_set_temp_min, 
                    occ_flex_set_temp_max, non_occ_flex_set_temp_min, non_occ_flex_set_temp_max, operation_mode, 
                    zone_set_temp_heat_name, zone_set_temp_cool_name, shed_counter_dict, zone, shed_initial_adjust, 
                    shed_dev_threshold, shed_delta_ratchet, hands_off_zone, zone_name, vav_damper_set, vav_discharge_temp, 
                    vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set, schedule_price, schedule_occupancy, 
                    occ_min_threshold, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule, 
                    demand_decrease_cap, demand_decrease, demand_decrease_error, demand_decrease_error_min,
                    shift_counter_dict, shift_price_occ_event, shift_horizon_time, shift_single_step_adjs_zone,
                    shift_check_demand, baseline_demand_peak, current_demand, peak_demand_diff_error_min, 
                    deadband_peak_demand_diff_error_min, reduce_VAV, shift_target_demand_mod, shift_adjust, shift_dev_threshold):

    '''Compute the control output based on measurement and forecast values.
    
        Parameters
        ----------

        shed_price_event : function
            Function used to identify if DF shed control must be executed based on price event.

        shed_savings_mode : function
            Function that triggers a savings mode when there is no occupancy.

        shed_single_step_adj_zone : function
            Function that controls the shedding of heating and cooling loads.

        shed_perform_target_ratch : function
            Function that applies a ratchet mechanism to progressively increase the shed amount for heating and cooling based on predefined conditions if current demand has reach the target.

        zone_qualification_check : function
            Function used to determine which zones qualify for shedding based on current conditions.
        
        rebound_management_zone : function
            Function that applies rebound with ratchet mechanism to progressively go back to baseline control.

        zone_temp : int or float
            Contains the current temperature value of the zone.

        zone_set_temp_heat : int or float
            Contains the setpoint value for heating in the zone.

        zone_set_temp_cool : int or float
            Contains the setpoint value for cooling in the zone.

        price_threshold_value : int or float
            Contains the threshold value for price to trigger events.

        occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during occupancy.

        occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during occupancy.

        non_occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during non-occupancy.

        non_occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during non-occupancy.

        operation_mode : str 
            Contains the value representing the current operation mode.

        zone_set_temp_heat_name : str
            Contains the value representing the name of the heating setpoint for the zone.

        zone_set_temp_cool_name : str
            Contains the value representing the name of the cooling setpoint for the zone.

        shed_counter_dict : dict
            Contains the counter values for shed events.

        zone : int or float
            Contains the value representing the zone identifier.

        shed_initial_adjust : int or float
            Contains the initial adjustment value for shedding.

        shed_dev_threshold : int or float
            Contains the deviation threshold value for shedding.

        shed_delta_ratchet : int or float
            Contains the delta ratchet value for shedding adjustments.

        hands_off_zone : str
            Contains the name of the zones that are in hands-off mode.

        zone_name : string
            Contains the value representing the name of the zone.

        vav_damper_set : int or float
            Contains the setpoint value for the VAV damper.

        vav_discharge_temp : int or float
            Contains the discharge temperature value from the VAV.

        vav_reheat_command : int or float
            Contains the command value for VAV reheat.

        ahu_supply_temp : int or float
            Contains the supply temperature value from the AHU.

        ahu_supply_flow : int or float
            Contains the supply flow value from the AHU.

        ahu_supply_flow_set : int or float
            Contains the setpoint value for AHU supply flow.

        schedule_price : int or float
            Contains the scheduled price value.

        schedule_occupancy : int or float
            Contains the scheduled occupancy value.

        occ_min_threshold : int or float
            Contains the minimum threshold value for occupancy.

        zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.

        demand_decrease_cap : int or float
            Contains the objective demand decrease.

        demand_decrease : int or float
            Contains the current demand decrease value.

        demand_decrease_error : int or float
            Contains the difference between DDcap and current building demand.

        demand_decrease_error_min : int or float
            Contains the minimum allowable difference between DDcap and current building demand.
        
        shift_counter_dict : dict
            Contains the counter values for shift events.

        shed_price_occ_event : function
            Function used to identify if DF shed control must be executed based on price event.
        
        shift_horizon_time : int
            Contains start time of the shift period. Multiply hours by 4 for 15-minute intervals, by 2 for 30-minute intervals, etc. 
        
        shift_single_step_adjs_zone : function
            Function that controls the shifting of heating and cooling loads.
        
        shift_check_demand : function 
            Function used to check if current demand requires modulation. 
        
        baseline_demand_peak : int or float
            Contains baseline demand peak value across the simulated period.

        current_demand : int or float
            Contains the current demand value.
        
        peak_demand_diff_error_min : int or float
            Contains the predefined minimum peak demand difference error.
        
        deadband_peak_demand_diff_error_min: int or float
            Contains the predefined minimum deadband peak peak demand difference error.
        
        reduce_VAV: XXXXXXXXXXXXX
            XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        
        shift_target_demand_mod : function
            Function used to modulate the demand to a target demand decrease from baseline peak.

        shift_adjust : int or float
            Contains the current temperature adjusment value allowed for the shifting.

        shift_dev_threshold : int or float
            Contains the value of the shift threshold for zone temperature deviation from effective setpoint.
        
        Returns
        -------
        
        shed_counter_dict[zone] :  dict
            Contains the counter values for shed events per zone.

        ratcheting_list :
            Contains the names of the zones currently eligible for performing ratchet adjustments..

        rebound_heat_list : 
            Contains the names of the zones currently eligible for performing rebound for heating.

        rebound_cool_list :
            Contains the names of the zones currently eligible for performing rebound for cooling.

        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
    control_results = {}  
    ratcheting_list = {}
    rebound_heat_list = {}
    rebound_cool_list = {}
    ratcheting_list_unshift = {}

    if zone not in shed_counter_dict:
        shed_counter_dict[zone] = 0
    print(zone, shed_counter_dict[zone])

    if zone not in shift_counter_dict:
        shift_counter_dict[zone] = 0
    print(zone, shift_counter_dict[zone])

    if shift_price_occ_event (schedule_price, schedule_occupancy, price_threshold_value, occ_min_threshold, shift_horizon_time):

        reduce_VAV = shift_check_demand(baseline_demand_peak, current_demand, peak_demand_diff_error_min, deadband_peak_demand_diff_error_min)
        
        if reduce_VAV == 0 and zone_qualification_check (operation_mode, zone_temp,  schedule_occupancy, occ_min_threshold, occ_flex_set_temp_min, occ_flex_set_temp_max, non_occ_flex_set_temp_min, non_occ_flex_set_temp_max,
                            hands_off_zone, zone_name, zone_set_temp_heat, zone_set_temp_cool, vav_damper_set, vav_discharge_temp, vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set): 
            print("qualified zone")
                                                                       
            # Compute shift
            new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list, shift_counter = shift_single_step_adjs_zone (operation_mode, zone_set_temp_heat, zone_set_temp_cool, shift_adjust, shift_dev_threshold, zone_temp,  
                        ratcheting_list, zone_set_temp_heat_name, zone_set_temp_cool_name, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule, shift_horizon_time)
            if zone_set_temp_heat is not None:
                control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
            if zone_set_temp_cool is not None:
                control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool
            shift_counter_dict[zone] = shift_counter  

        elif reduce_VAV == 1:
            new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list_unshift = shift_target_demand_mod (operation_mode, zone_set_temp_heat, zone_set_temp_cool, shift_adjust, zone_temp,  
                         ratcheting_list_unshift, zone_set_temp_heat_name, zone_set_temp_cool_name, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule, shift_horizon_time)
            if zone_set_temp_heat is not None:
                control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
            if zone_set_temp_cool is not None:
                control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool
        
        else:
            shift_counter_dict[zone] = 0
            if zone_set_temp_heat is not None:
                control_results [zone_set_temp_heat_name] = zone_set_temp_heat_bas_schedule[0] 
            if zone_set_temp_cool is not None:
                control_results [zone_set_temp_cool_name] = zone_set_temp_cool_bas_schedule[0] 
            print("no qualify, baseline setpoint", control_results) 

    elif shed_price_event(schedule_price, price_threshold_value):

        if schedule_occupancy [0] <= occ_min_threshold:
            print("savings mode")
            shed_counter_dict[zone] = 0
            new_zone_set_temp_heat, new_zone_set_temp_cool = shed_savings_mode (zone_set_temp_heat, zone_set_temp_cool, occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule)
            if zone_set_temp_heat is not None:
                control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
            if zone_set_temp_cool is not None:
                control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool 
        
        elif zone_qualification_check (operation_mode, zone_temp,  schedule_occupancy, occ_min_threshold, occ_flex_set_temp_min, occ_flex_set_temp_max, non_occ_flex_set_temp_min, non_occ_flex_set_temp_max,
                            hands_off_zone, zone_name, zone_set_temp_heat, zone_set_temp_cool, vav_damper_set, vav_discharge_temp, vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set): 
            print("qualified zone")
                                                                       
            if shed_counter_dict[zone] == 0:
                new_zone_set_temp_heat, new_zone_set_temp_cool, shed_counter = shed_single_step_adj_zone (operation_mode, zone_set_temp_heat, zone_set_temp_cool, shed_initial_adjust, 
                                occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule)
                if zone_set_temp_heat is not None:
                    control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
                if zone_set_temp_cool is not None:
                    control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool 
                shed_counter_dict[zone] = shed_counter
            
            else:
                new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list = shed_perform_target_ratch (demand_decrease_cap, demand_decrease, demand_decrease_error, demand_decrease_error_min,
                                operation_mode, zone_temp, zone_set_temp_heat, zone_set_temp_cool, 
                                occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                               shed_dev_threshold, shed_delta_ratchet, ratcheting_list, zone_set_temp_cool_name, zone_set_temp_heat_name)
                if zone_set_temp_heat is not None:
                    control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
                if zone_set_temp_cool is not None:
                    control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool

        else:
            shed_counter_dict[zone] = 0
            if zone_set_temp_heat is not None:
                control_results [zone_set_temp_heat_name] = zone_set_temp_heat_bas_schedule[0] 
            if zone_set_temp_cool is not None:
                control_results [zone_set_temp_cool_name] = zone_set_temp_cool_bas_schedule[0] 
            print("no qualify, baseline setpoint", control_results) 

    elif shed_counter_dict[zone] == 1:
        # Compute rebound management
        new_zone_set_temp_heat, new_zone_set_temp_cool, rebound_heat_list, rebound_cool_list, shed_counter = rebound_management_zone (zone_temp, zone_set_temp_heat, zone_set_temp_cool, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                                   rebound_heat_list, rebound_cool_list, zone_set_temp_heat_name, zone_set_temp_cool_name, shed_delta_ratchet)
        if zone_set_temp_heat is not None:
            control_results [zone_set_temp_heat_name] = new_zone_set_temp_heat
        if zone_set_temp_cool is not None:
            control_results [zone_set_temp_cool_name] = new_zone_set_temp_cool 
        shed_counter_dict[zone] = shed_counter 
        print("rebound shed", control_results)

    else:
        # Compute baseline min/max temperature sepoints
        shed_counter_dict[zone] = 0
        if zone_set_temp_heat is not None:
            control_results [zone_set_temp_heat_name] = zone_set_temp_heat_bas_schedule[0]
        if zone_set_temp_cool is not None:
            control_results [zone_set_temp_cool_name] = zone_set_temp_cool_bas_schedule[0] 
        print("no shed, baseline setpoint", control_results)       
    
    print(ratcheting_list)
    return shed_counter_dict[zone], shift_counter_dict[zone], ratcheting_list, rebound_heat_list, rebound_cool_list, control_results, reduce_VAV, ratcheting_list_unshift
                                            
def sparql_query(graph_path, query_paths):

    '''Query identifiers for control points per zone from the selected graph path.

        Parameters
        ----------            

        graph_path : str
            Contains the path to the graph directory.
        
        query_paths : str
            Contains the paths to the sparql queries.

        Returns
        -------

        number_of_zones : int
            Contains the length of the query results, ie the number of zones with sufficient points from the graph. 

        zone_names : str
            Contains the names of the zones.

        zone_temp_point : str
            Contains the identifier for the temperature measurement point per zone.

        zone_set_temp_point : str
            Contains the identifier for the setpoint temperature measurement per zone.

        zone_set_temp_heat_point : str
            Contains the identifier for the heating setpoint temperature measurement per zone.

        zone_set_temp_cool_point : str
            Contains the identifier for the cooling setpoint temperature measurement per zone.

        set_temp_min_point : str
            Contains the identifier for the minimum setpoint temperature measurement.

        set_temp_max_point : str
            Contains the identifier for the maximum setpoint temperature measurement.

        occ_sensor_point : str
            Contains the identifier for the occupancy sensor point.

        vav_damper_set_point : str
            Contains the identifier for the VAV damper setpoint.

        vav_discharge_temp_point : str
            Contains the identifier for the VAV discharge temperature measurement point.

        vav_reheat_command_point : str
            Contains the identifier for the VAV reheat command point.

        ahu_supply_temp_point : str
            Contains the identifier for the AHU supply temperature measurement point.

        ahu_supply_flow_point : str
            Contains the identifier for the AHU supply flow measurement point.

        ahu_supply_flow_set_point : str
            Contains the identifier for the AHU supply flow setpoint.

        ele_pow_point : str
            Contains the identifier for the electric power sensor.

        therm_pow_point : str
            Contains the identifier for the thermal power sensor.


    '''      

    from rdflib.plugins.sparql import prepareQuery
    import rdflib
    from rdflib import Namespace
    
    # Query the identifiers for control points per zone    
    g = rdflib.Graph()
    g.parse(graph_path)

    # Create lists for the identifiers needed to instatiate the required data points 
    zone_temp_point = []
    zone_set_temp_point = []
    zone_set_temp_heat_point = []
    zone_set_temp_cool_point = []
    set_temp_min_point = []
    set_temp_max_point  = []
    occ_sensor_point  = []    
    zone_names = []
    vav_damper_set_point = []
    vav_discharge_temp_point = [] 
    vav_reheat_command_point = []
    ahu_supply_temp_point = None
    ahu_supply_flow_point = None
    ahu_supply_flow_set_point = None
    ele_pow_point = []
    therm_pow_point = []

    # Iterate over the query paths and execute each query
    for query_path in query_paths:
        with open(query_path) as f:
            query_text = f.read()
        
        # Execute the query
        qres = g.query(query_text)

        # Process the results
        for row in qres:
            print(str(row))
            
            zone_temp_point_value = getattr(row, 'zone_temp_point', None)
            zone_set_temp_point_value = getattr(row, 'zone_set_temp_point', None)

            zone_set_temp_heat_point_value = getattr(row, 'zone_set_temp_heat_point', None)
            zone_set_temp_cool_point_value = getattr(row, 'zone_set_temp_cool_point', None)

            set_temp_min_point_value = getattr(row, 'set_temp_min_point', None)
            set_temp_max_point_value = getattr(row, 'set_temp_max_point', None)

            occ_sensor_point_value = getattr(row, 'occ_sensor_point', None)
            vav_damper_set_point_value = getattr(row, 'vav_damper_set_point', None)

            vav_discharge_temp_point_value = getattr(row, 'vav_discharge_temp_point', None)
            vav_reheat_command_point_value = getattr(row, 'vav_reheat_command_point', None)

            zone_names_value = getattr(row, 'zone', None)

            ahu_supply_temp_point_value = getattr(row, 'ahu_supply_temp_point', None)
            ahu_supply_flow_point_value = getattr(row, 'ahu_supply_flow_point', None)
            ahu_supply_flow_set_point_value = getattr(row, 'ahu_supply_flow_set_point', None)


            ele_pow_point_value = getattr(row, 'ele_pow_point', None)
            therm_pow_point_value = getattr(row, 'therm_pow_point', None)


            if zone_temp_point_value is not None:
                zone_temp_point.append(str(zone_temp_point_value))
            if zone_set_temp_point_value is not None:
                zone_set_temp_point.append(str(zone_set_temp_point_value))
            
            if zone_set_temp_heat_point_value is not None:
                zone_set_temp_heat_point.append(str(zone_set_temp_heat_point_value))
            if zone_set_temp_cool_point_value is not None:
                zone_set_temp_cool_point.append(str(zone_set_temp_cool_point_value))

            if set_temp_min_point_value is not None:
                set_temp_min_point.append(str(set_temp_min_point_value))
            if set_temp_max_point_value is not None:
                set_temp_max_point.append(str(set_temp_max_point_value))
            
            if occ_sensor_point_value is not None:
                occ_sensor_point.append(str(occ_sensor_point_value))

            if vav_damper_set_point_value is not None:
                vav_damper_set_point.append(str(vav_damper_set_point_value))
            if vav_discharge_temp_point_value is not None:
                vav_discharge_temp_point.append(str(vav_discharge_temp_point_value))
            if vav_reheat_command_point_value is not None:
                vav_reheat_command_point.append(str(vav_reheat_command_point_value))
            
            if zone_names_value is not None:
                zone_names.append(str(zone_names_value))

            if ahu_supply_temp_point_value is not None:
                ahu_supply_temp_point = (str(ahu_supply_temp_point_value))
            if ahu_supply_flow_point_value is not None:
                ahu_supply_flow_point = (str(ahu_supply_flow_point_value))
            if ahu_supply_flow_set_point_value is not None:
                ahu_supply_flow_set_point = (str(ahu_supply_flow_set_point_value))
            
            if ele_pow_point_value is not None and str(ele_pow_point_value) not in ele_pow_point:
                ele_pow_point.append(str(ele_pow_point_value))
                
            if therm_pow_point_value is not None and str(therm_pow_point_value) not in therm_pow_point:
                therm_pow_point.append(str(therm_pow_point_value))


    number_of_zones = range(len(zone_names))
    return number_of_zones, zone_names, zone_temp_point, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, set_temp_min_point, set_temp_max_point, occ_sensor_point, vav_damper_set_point, vav_discharge_temp_point, vav_reheat_command_point, ahu_supply_temp_point, ahu_supply_flow_point, ahu_supply_flow_set_point, ele_pow_point, therm_pow_point 
 