def runaway_TsetHeaZon(TSetMin_baseline, TSetHeaZon, TSet_adj_current):
    '''Compute the runaway correction to adjust the zone heating temperature setpoint.
    
        Parameters
        ----------
        TSetMin_baseline : int 
            Contains the value of the current iteration for the minimum temperature of the baseline comfort range.

        TSetHeaZon : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

        Returns
        -------
        new_TsetHeaZon : int
            Defines the new value for zone heating temperature setpoint.
    
        '''
    # Release DR control (compute baseline min (heat) setpoints), in case there is a change of occupancy and the temperature difference is high (estimated 5 degrees now)
    if TSetMin_baseline - TSetHeaZon > 5:
        new_TsetHeaZon = TSetMin_baseline
    # Instead of realease DR, incremently reduce the last shed adjustment for heating       
    elif TSetHeaZon + TSet_adj_current < TSetMin_baseline:
        new_TsetHeaZon = TSetHeaZon + TSet_adj_current
    else:
        new_TsetHeaZon = TSetMin_baseline
    
    return new_TsetHeaZon