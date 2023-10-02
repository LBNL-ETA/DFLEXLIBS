def shed_TsetHeaZon (TsetHeaZon, TSet_adj_current, TSetMin, current_occ_status, current_occ_schedule, occ_min_threshold):

    '''Compute the shed control to adjust the zone heating temperature setpoint.
    
        Parameters
        ----------
        TSetHeaZon : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        TSetMin : int
            Contains the value of the current iteration for the minimum temperature of the comfort range.

        current_occ_status : int 
            Contains the value of the future iteration for the occupancy status. 

        current_occ_schedule : int 
            Contains the value of the future iteration for the occupancy schedule. 

        occ_min_threshold : int
            Contains the minimum occupancy value detected in the schedule list.
            
        Returns
        -------
        new_TsetHeaZon : int
            Defines the new value for zone heating temperature setpoint.
    
        '''
  
    # Compute DR shed control (for heating) 
    if (current_occ_status == occ_min_threshold and current_occ_schedule == occ_min_threshold):
        new_TsetHeaZon =  TSetMin 

    elif TsetHeaZon - TSet_adj_current > TSetMin:
        new_TsetHeaZon =  TsetHeaZon - TSet_adj_current
                                    
    else:
        new_TsetHeaZon =   TSetMin       
   
    return new_TsetHeaZon