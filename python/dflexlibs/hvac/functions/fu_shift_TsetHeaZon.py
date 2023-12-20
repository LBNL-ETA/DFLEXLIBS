def shift_TsetHeaZon (TsetHeaZon, TSet_adj_current, future_TSetMin_baseline):

    '''Compute the shift control to adjust the zone heating temperature setpoint.
    
        Parameters
        ----------
        TSetHeaZon : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        TSetMax : int 
            Contains the value of the current iteration for the maximum temperature of the comfort range.

        Returns
        -------
        new_TsetHeaZon : int
            Defines the new value for zone heating temperature setpoint.
    
        '''
    
    # Compute DR shift control (for heating) 
    
    if TsetHeaZon < future_TSetMin_baseline + TSet_adj_current:
        new_TsetHeaZon =  future_TSetMin_baseline + TSet_adj_current
                                    
    else:
        new_TsetHeaZon =  TsetHeaZon 
    
    return new_TsetHeaZon