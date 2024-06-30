def shift_heat_cool_temp_zone (operation_mode, zone_set_temp_heat, zone_set_temp_cool, shift_adjust, shift_dev_threshold, zone_temp,  
                        ratcheting_list, zone_set_temp_heat_name, zone_set_temp_cool_name, zone_set_temp_heat_bas_schedule, 
                        zone_set_temp_cool_bas_schedule, shift_horizon_time):
                
    
    '''Compute the shift control to adjust the zone heating and cooling temperature setpoint.
    
        Parameters
        ----------
        operation_mode : str 
            Contains the value representing the current operation mode.

        zone_set_temp_heat : int or float
            Contains the setpoint value for heating in the zone.

        zone_set_temp_cool : int or float
            Contains the setpoint value for cooling in the zone.

        shift_adjust : int or float
            Contains the current temperature adjusment value allowed for the shifting.

        shift_dev_threshold : int or float
            Contains the value of the shift threshold for zone temperature deviation from effective setpoint.

        zone_temp : int or float
            Contains the current temperature value of the zone.

        ratcheting_list : list
            Contains the names of the zones to be ratchet.

        zone_set_temp_heat_name : str
            Contains the value representing the name of the heating setpoint for the zone.

        zone_set_temp_cool_name : str
            Contains the value representing the name of the cooling setpoint for the zone.
 
        zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.

        shift_horizon_time : int
            Contains start time of the shift period. Multiply hours by 4 for 15-minute intervals, by 2 for 30-minute intervals, etc.    
            
        Returns
        -------
        new_zone_set_temp_heat : int or float
            Defines the new value for zone heating temperature setpoint.

        new_zone_set_temp_cool : int or float
            Defines the new value for zone cooling temperature setpoint.

        ratcheting_list : list
            Updates the list with the name of the zones to be ratchet.  
    
    '''
    
    dev_heat = dev_cool = None
    new_zone_set_temp_heat = None
    new_zone_set_temp_cool = None

    # Check the HVAC operation (heating/cooling) mode
    if operation_mode == 'heat':  
        if zone_set_temp_heat is not None:
            
            if shift_horizon_time < len(zone_set_temp_heat_bas_schedule):
                future_TSetHeaZon_baseline = zone_set_temp_heat_bas_schedule[shift_horizon_time]
            else:
                future_TSetHeaZon_baseline = zone_set_temp_heat_bas_schedule[0]
            
            # considers future baseline value, otherwise when occ=0 TSetHeaZon is min, and the control does not preheat enough
            # dev prioritizes/filters hotter zones, to have more potential for shed
            
            dev_heat = (future_TSetHeaZon_baseline + shift_adjust) - zone_temp
            if dev_heat > shift_dev_threshold: 
                shift_counter = 1 
                if zone_set_temp_heat != future_TSetHeaZon_baseline + shift_adjust:
                    ratcheting_list [zone_set_temp_heat_name[:-1]] = dev_heat    
                    new_zone_set_temp_heat =  future_TSetHeaZon_baseline + shift_adjust
                    print("shift heat")
                else:
                    new_zone_set_temp_heat = zone_set_temp_heat
                    print("keep shift")

            # to consider the cases where shift already started or that we unshift to future value and 
            # need to keep it to avoid going back to baseline (min value) 
            elif (zone_set_temp_heat == future_TSetHeaZon_baseline + shift_adjust) or zone_set_temp_heat == future_TSetHeaZon_baseline:
                shift_counter = 1
                new_zone_set_temp_heat = zone_set_temp_heat
                print("keep shift")
                        
            else:
                new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
                shift_counter = 0
                print("no shift, baseline setpoint") 

        if zone_set_temp_cool is not None:
            new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
        

    else:
        if zone_set_temp_cool is not None:
            
            if shift_horizon_time < len(zone_set_temp_cool_bas_schedule):
                future_TSetHeaZon_baseline = zone_set_temp_cool_bas_schedule[shift_horizon_time]
            else:
                future_TSetCooZon_baseline = zone_set_temp_cool_bas_schedule[0]
            
            # considers future baseline value, otherwise when occ=0 TSetCooZon is max, so the control does not precool enough
            # dev prioritizes/filters warmer zones, to have more potential for shed
            dev_cool = zone_temp - (future_TSetCooZon_baseline - shift_adjust)
            if dev_cool > shift_dev_threshold:
                shift_counter = 1
                if zone_set_temp_cool != future_TSetCooZon_baseline - shift_adjust:
                    ratcheting_list [zone_set_temp_cool_name[:-1]] = dev_cool
                    new_zone_set_temp_cool =  future_TSetCooZon_baseline - shift_adjust
                    print("shift cool")
                else:
                    new_zone_set_temp_cool = zone_set_temp_cool
                    print("keep shift") 
            
            elif (zone_set_temp_cool == future_TSetCooZon_baseline - shift_adjust) or zone_set_temp_cool == future_TSetCooZon_baseline:
                shift_counter = 1
                new_zone_set_temp_cool = zone_set_temp_cool
                print("keep shift") 

            else:
                new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule
                shift_counter = 0
                
                print("no shift, baseline setpoint") 
                
        if zone_set_temp_heat is not None:
            new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]

            
    return new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list, shift_counter