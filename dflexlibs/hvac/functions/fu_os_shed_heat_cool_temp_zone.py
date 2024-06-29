def shed_heat_cool_temp_zone (operation_mode, zone_set_temp_heat, zone_set_temp_cool, shed_initial_adjust, 
                                occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule):
    '''Compute the shed control to adjust the zone heating and cooling temperature setpoint.
    
        Parameters
        ----------
        operation_mode : int 
            Contains the value representing the current operation mode.

        zone_set_temp_heat : int or float
            Contains the setpoint value for heating in the zone.

        zone_set_temp_cool : int or float
            Contains the setpoint value for cooling in the zone.

        shed_initial_adjust : int or float
            Contains the initial adjustment value for shedding.

        occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during occupancy.

        occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during occupancy.

        zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.
                
        Returns
        -------
        new_zone_set_temp_heat : int or float
            Defines the new value for zone heating temperature setpoint.

        new_zone_set_temp_cool : int or float
            Defines the new value for zone cooling temperature setpoint.

        shed_counter : int
            Defines an indicator of whether a shed has occurred for the specific zone in the current iteration. 
    
    '''
  
    new_zone_set_temp_heat = None
    new_zone_set_temp_cool = None

    if operation_mode == 'heat':

        if zone_set_temp_heat is not None:
            if zone_set_temp_heat - shed_initial_adjust > occ_flex_set_temp_min:
                new_zone_set_temp_heat =  zone_set_temp_heat - shed_initial_adjust
                shed_counter = 1
                print("first shed heat")
            #for conditions when TSetHeaZon & TSetMin_baseline are at min (eg 12C) but occ is 1 and price is high so shed is activated 
            #but if we use the equation above the new setpoint would be too low (eg 12C - shed_initial_adjust)
            #or conditions when shed_max_offset (the one that defines TSetMin_shed) is set to a value lower than shed_initial_adjust
            else:
                new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
                shed_counter = 0
                print("no shed, min TSetHeaZon")
        if zone_set_temp_cool is not None:
            new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
        
    else:
        if zone_set_temp_cool is not None:
            
            if zone_set_temp_cool + shed_initial_adjust < occ_flex_set_temp_max:
                new_zone_set_temp_cool =  zone_set_temp_cool + shed_initial_adjust
                shed_counter = 1
                print("first shed cool")
            #for conditions when TSetCooZon & TSetMax_baseline are at max (eg 30C) but occ is 1 and price is high so shed is activated 
            #but if we use the equation above the new setpoint would be too high (eg 30C + shed_initial_adjust)  
            #or conditions when shed_max_offset (the one that defines TSetMax_shed) is set to a value lower than shed_initial_adjust
            else:
                new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
                shed_counter = 0
                print("no shed, baseline setpoint")
        if zone_set_temp_heat is not None:
            new_zone_set_temp_heat =  zone_set_temp_heat_bas_schedule[0]
        
    return new_zone_set_temp_heat, new_zone_set_temp_cool, shed_counter


       