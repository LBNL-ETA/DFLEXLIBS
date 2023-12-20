def shed_TsetCooZon (TsetCooZon, TSet_adj_current, TSetMax, current_occ_status, current_occ_schedule, occ_min_threshold):

    '''Compute the shed control to adjust the zone cooling temperature setpoint.
    
        Parameters
        ----------
        TSetCooZon : int
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        TSetMax : int 
            Contains the value of the current iteration for the maximum temperature of the comfort range.

        current_occ_status : int 
            Contains the value of the future iteration for the occupancy status. 

        current_occ_schedule : int 
            Contains the value of the future iteration for the occupancy schedule. 

        occ_min_threshold : int
            Contains the minimum occupancy value detected in the schedule list.
            
        Returns
        -------
        new_TsetCooZon : int
            Defines the new value for zone cooling temperature setpoint.
    
        '''
  
    # Compute DR shed control (for cooling) 
    if (current_occ_status == occ_min_threshold and current_occ_schedule == occ_min_threshold):
        new_TsetCooZon =  TSetMax

    elif TsetCooZon + TSet_adj_current < TSetMax:
        new_TsetCooZon =  TsetCooZon + TSet_adj_current
                                    
    else:
        new_TsetCooZon =  TSetMax 
                
    return new_TsetCooZon