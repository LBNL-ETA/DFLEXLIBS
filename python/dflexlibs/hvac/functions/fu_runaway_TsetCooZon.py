def runaway_TsetCooZon(TSetMax_baseline, TSetCooZon, TSet_adj_current):
    '''Compute the runaway correction to adjust the zone cooling temperature setpoint.
    
        Parameters
        ----------
        TSetMax_baseline : int 
            Contains the value of the current iteration for the maximum temperature of the baseline comfort range.

        TSetCooZon : int
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        Returns
        -------
        new_TsetCooZon : int
            Defines the new value for zone cooling temperature setpoint.
    
        '''
    # Release DR control (compute baseline max (cool) setpoints), in case there is a change of occupancy and the temperature difference is high (estimated 5 degrees now)
    if TSetCooZon - TSetMax_baseline > 5:
        new_TsetCooZon = TSetMax_baseline
    # Instead of realease DR, incremently reduce the last shed adjustment for cooling       
    elif TSetCooZon - TSet_adj_current > TSetMax_baseline:
        new_TsetCooZon = TSetCooZon - TSet_adj_current
    else:
        new_TsetCooZon = TSetMax_baseline
    
    return new_TsetCooZon