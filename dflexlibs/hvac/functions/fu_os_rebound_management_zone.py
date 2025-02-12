def rebound_management_zone(zone_temp, zone_set_temp_heat, zone_set_temp_cool, zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule,
                                   rebound_heat_list, rebound_cool_list, zone_set_temp_heat_name, zone_set_temp_cool_name, shed_delta_ratchet):


    '''Compute a rebound strategy when shed event is finished.
    
        Parameters
        ----------
        zone_temp : int or float
            Contains the value of the current iteration for the zone temperature measurement. 

        zone_set_temp_heat : int or float
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        zone_set_temp_cool : int or float
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

         zone_set_temp_heat_bas_schedule : list
            Contains the baseline schedule value for heating setpoint in the zone.

        zone_set_temp_cool_bas_schedule : list
            Contains the baseline schedule value for cooling setpoint in the zone.

        rebound_list : list
            Contains the names of the zones to run the rebound strategy.

        zone_set_temp_heat_name : str
            Contains the name of the zone temperature heating setpoint.

        zone_set_temp_cool_name : str
            Contains the name of the zone temperature cooling setpoint.

        shed_delta_ratchet : int or float
            Contains the value of the incremental delta for ratcheting the zone temperature setpoint.
            
        Returns
        -------
        new_zone_set_temp_heat : int or float
            Defines the new value for zone heating temperature setpoint.

        new_zone_set_temp_cool : int or float
            Defines the new value for zone cooling temperature setpoint.

        rebound_list : list
            Updates the list with the names of the zones to run the rebound strategy. 

        shed_counter : int
            Update shed counter (an indicator of whether a shed has occurred for the specific zone in the current iteration).
    
    '''


    dev_heat = dev_cool = None
    new_zone_set_temp_heat = new_zone_set_temp_cool = None
    heat_shed_counter = None
    cool_shed_counter = None

    if zone_set_temp_heat is not None:
        dev_heat = zone_temp - zone_set_temp_heat
        
        if not zone_set_temp_heat == zone_set_temp_heat_bas_schedule[0]:
            rebound_heat_list [zone_set_temp_heat_name] = dev_heat  
            if zone_set_temp_heat + shed_delta_ratchet < zone_set_temp_heat_bas_schedule[0]:
                new_zone_set_temp_heat = zone_set_temp_heat + shed_delta_ratchet
                heat_shed_counter = 1
            else:
                new_zone_set_temp_heat = zone_set_temp_heat_bas_schedule[0]
                heat_shed_counter = 0 
            
        else:
            heat_shed_counter = 0
            new_zone_set_temp_heat = zone_set_temp_heat           

    if zone_set_temp_cool is not None:
        dev_cool = zone_set_temp_cool - zone_temp
        if not zone_set_temp_cool == zone_set_temp_cool_bas_schedule[0]:
            rebound_cool_list [zone_set_temp_cool_name] = dev_cool
            if zone_set_temp_cool - shed_delta_ratchet > zone_set_temp_cool_bas_schedule[0]:
                new_zone_set_temp_cool = zone_set_temp_cool - shed_delta_ratchet
                cool_shed_counter = 0
            else:
                new_zone_set_temp_cool = zone_set_temp_cool_bas_schedule[0]
                cool_shed_counter = 1
        else:
            cool_shed_counter = 0
            new_zone_set_temp_cool = zone_set_temp_cool
        
    if heat_shed_counter == 1 or cool_shed_counter == 1:
        shed_counter = 1
    else:
        shed_counter = 0
                         
    return new_zone_set_temp_heat, new_zone_set_temp_cool, rebound_heat_list, rebound_cool_list, shed_counter