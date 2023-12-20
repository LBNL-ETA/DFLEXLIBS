def shift_TsetCooZon (TsetCooZon, TSet_adj_current, future_TSetMax_baseline):

    '''Compute the shift control to adjust the zone cooling temperature setpoint.
    
        Parameters
        ----------
        TSetCooZon : int
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        TSetMin : int 
            Contains the value of the current iteration for the minimum temperature of the comfort range.

        Returns
        -------
        new_TsetCooZon : int
            Defines the new value for zone cooling temperature setpoint.
    
        '''
    
    # Compute DR shift control (for cooling) 

    if TsetCooZon > future_TSetMax_baseline - TSet_adj_current:
        new_TsetCooZon =  future_TSetMax_baseline - TSet_adj_current
                                    
    else:
        new_TsetCooZon =  TsetCooZon 
    
    return new_TsetCooZon