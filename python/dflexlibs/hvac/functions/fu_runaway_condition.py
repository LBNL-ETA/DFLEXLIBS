def runaway_condition (TZon, TSetMin, TSetMax):
    
    '''Define whether to release DR control (compute baseline control) or not.
    
        Parameters
        ----------
        TZon : int
            Contains the value of the current iteration for the zone temperature measurement. 

        TSetMin : int 
            Contains the value of the current iteration for the minimum temperature of the comfort range.

        TSetMax : int 
            Contains the value of the current iteration for the maximum temperature of the comfort range.

        Returns
        -------
        releaseDR : boolean
            Contains a value to define whether to release DR control (compute baseline control) or not.

        '''

    if TZon < TSetMin or TZon > TSetMax:
        # Release DR control (compute baseline control)
        releaseDR = True              
        return releaseDR  
    else:
        releaseDR = False
        return releaseDR