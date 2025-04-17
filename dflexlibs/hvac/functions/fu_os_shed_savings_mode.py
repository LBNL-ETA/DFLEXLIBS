def shed_savings_mode (zone_set_temp_heat, zone_set_temp_cool, non_occ_flex_set_temp_min, non_occ_flex_set_temp_max, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule):

    '''Triggers a savings mode when there is no occupancy.
    
        Parameters
        ----------
       
        zone_set_temp_heat : int or float
            Contains the setpoint value for heating in the zone.

        zone_set_temp_cool : int or float
            Contains the setpoint value for cooling in the zone.

        non_occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during non occupancy.

        non_occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during non occupancy.

        zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.
        
            
        Returns
        -------

        new_zone_set_temp_heat : int
            Defines the new value for zone heating temperature setpoint.
    
        new_zone_set_temp_cool : int
            Defines the new value for zone cooling temperature setpoint.
    

    
        '''
    new_zone_set_temp_heat = None
    new_zone_set_temp_cool = None
    
    if zone_set_temp_heat is not None:
        if zone_set_temp_heat_bas_schedule[0] > non_occ_flex_set_temp_min:
            new_zone_set_temp_heat = non_occ_flex_set_temp_min   
            shed_counter = 1
        else:    
            new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
            shed_counter = 0
            

    if zone_set_temp_cool is not None:
        if zone_set_temp_cool_bas_schedule[0] < non_occ_flex_set_temp_max:
            new_zone_set_temp_cool = non_occ_flex_set_temp_max
            shed_counter = 1

        else:
            new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
            shed_counter = 0

    return new_zone_set_temp_heat, new_zone_set_temp_cool, shed_counter