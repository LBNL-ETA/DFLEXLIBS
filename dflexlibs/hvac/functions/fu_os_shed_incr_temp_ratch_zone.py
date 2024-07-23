def shed_incr_temp_ratch_zone (operation_mode, zone_temp, zone_set_temp_heat, zone_set_temp_cool, 
                                occ_flex_set_temp_min, occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                               shed_dev_threshold, shed_delta_ratchet, ratcheting_list, zone_set_temp_cool_name, zone_set_temp_heat_name):
    
    '''Compute a ratcheting strategy to further shed the zone heating and cooling temperature setpoint.
    
        Parameters
        ----------

        operation_mode : int 
            Contains the value representing the current operation mode.

        zone_temp : int or float
            Contains the current temperature value of the zone.

        zone_set_temp_heat : int or float
            Contains the setpoint value for heating in the zone.

        zone_set_temp_cool : int or float
            Contains the setpoint value for cooling in the zone.

        occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during occupancy.

        occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during occupancy.

        zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.
        
        shed_dev_threshold : int or float
            Contains the deviation threshold value for shedding.

        shed_delta_ratchet : int or float
            Contains the delta ratchet value for shedding adjustments.

        ratcheting_list :
            Contains the names of the zones currently eligible for performing ratchet adjustments..

        zone_set_temp_heat_name : string
            Contains the value representing the name of the heating setpoint for the zone.

        zone_set_temp_cool_name : string
            Contains the value representing the name of the cooling setpoint for the zone.

            
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
            
    print(new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list)
    return new_zone_set_temp_heat, new_zone_set_temp_cool, ratcheting_list