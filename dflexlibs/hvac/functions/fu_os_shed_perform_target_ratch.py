def shed_perform_target_ratch (demand_decrease_cap, demand_decrease, demand_decrease_error, demand_decrease_error_min, 
                        operation_mode, zone_temp, zone_set_temp_heat, zone_set_temp_cool, 
                        occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                        shed_dev_threshold, shed_delta_ratchet, ratcheting_list, zone_set_temp_cool_name, zone_set_temp_heat_name):

    '''Define .

        Parameters
        ----------            
        
        demand_decrease_cap : int or float
            Contains the objective demand decrease.

        demand_decrease : int or float
            Contains the current demand decrease value.

        demand_decrease_error : int or float
            Contains the difference between DDcap and current building demand.

        demand_decrease_error_min : int or float
            Contains the minimum allowable difference between DDcap and current building demand.
            
        Returns
        -------

        target_met : boolean
            Contains a value to define whether to the demand target has been met.


    '''    
    demand_decrease_error = demand_decrease_cap - demand_decrease 
    
    if  demand_decrease_error > demand_decrease_error_min:
        
        dev_heat = dev_cool = None
        new_zone_set_temp_heat = None
        new_zone_set_temp_cool = None

        # Check the HVAC operation (heating/cooling) mode
        if operation_mode == 'heat':

            print("heating season", "TSetHeaZon", zone_set_temp_heat)
            if zone_set_temp_heat is not None:
                # TSetHeaZon is already (TSetHeaZon - TSet_adj_current) from the first shed 
                dev_heat = zone_temp - (zone_set_temp_heat)
                print(dev_heat < shed_dev_threshold)
                        
                if dev_heat < shed_dev_threshold: 
                    if not zone_set_temp_heat == occ_flex_set_temp_min:
                        ratcheting_list [zone_set_temp_heat_name[:-1]] = dev_heat    
                    if zone_set_temp_heat  - shed_delta_ratchet >= occ_flex_set_temp_min: 
                        new_zone_set_temp_heat =  zone_set_temp_heat  - shed_delta_ratchet
                        print("ratcheting shed heat")
                    else:
                        new_zone_set_temp_heat = zone_set_temp_heat
                        print("continue shed")
                else:
                    new_zone_set_temp_heat = zone_set_temp_heat
                    print("continue shed") 
                    
            if zone_set_temp_cool is not None:
                new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
            print("TSetHeaZon", zone_set_temp_heat, "new_TSetHeaZon", new_zone_set_temp_heat)

        else:
            if zone_set_temp_cool is not None:
                # TSetCooZon is already (TSetCooZon + TSet_adj_current) from the first shed
                dev_cool = (zone_set_temp_cool) - zone_temp
                print(dev_cool, zone_set_temp_cool, zone_temp)
                print(dev_cool < shed_dev_threshold)
            
                if dev_cool < shed_dev_threshold:
                    if not zone_set_temp_cool == occ_flex_set_temp_max:
                        ratcheting_list [zone_set_temp_cool_name[:-1]] = dev_cool
                    if zone_set_temp_cool + shed_delta_ratchet <= occ_flex_set_temp_max: 
                        new_zone_set_temp_cool =  zone_set_temp_cool  + shed_delta_ratchet
                        print("ratcheting shed cool")
                    else:
                        new_zone_set_temp_cool = zone_set_temp_cool
                        print("continue shed")
                else:
                    new_zone_set_temp_cool = zone_set_temp_cool
                    print("continue shed") 

            if zone_set_temp_heat is not None:
                new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
            
    else:
        if operation_mode == 'heat':
            if zone_set_temp_heat is not None:
                new_zone_set_temp_heat = zone_set_temp_heat
        
            if zone_set_temp_cool is not None:
                    new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
            print("no ratchet, continue shed heat")

        else:
            if zone_set_temp_heat is not None:
                new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
        
            if zone_set_temp_cool is not None:
                    new_zone_set_temp_cool = zone_set_temp_cool
        print("no ratchet, continue shed cool")

    print(new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list)
    return new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list