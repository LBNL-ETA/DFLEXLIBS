def new_comfort_range (TSetMin_baseline, TSetMax_baseline, Tlimit_min, Tlimit_max, adjust_comfort_offset):
    
    '''Define the adjsted values for the minimum and maximum temperature for comfort range.
    
        Parameters
        ----------
        TSetMin_baseline : int 
            Contains the value of the current iteration for the minimum temperature of the baseline comfort range.

        TSetMax_baseline : int 
            Contains the value of the current iteration for the maximum temperature of the baseline comfort range.

        Tlimit_min : int
            Contains the temperature limit minimum that allows the HVAC system to operate.

        Tlimit_max : int
            Contains the temperature limit maximum that allows the HVAC system to operate.

        adjust_comfort_offset : int
            Contains allowed increase and decrease temperature offset from baseline comfort range.
      
        Returns
        -------
        TSetMin : int 
            Contains the adjusted value of the current iteration for the minimum temperature of the  comfort range.

        TSetMax : int 
            Contains the adjusted value of the current iteration for the maximum temperature of the  comfort range.

        '''
    if TSetMin_baseline == Tlimit_min:
        TSetMin = TSetMin_baseline # Keep minimum setpoint
    else: 
        TSetMin = TSetMin_baseline - adjust_comfort_offset # Adjust minimum setpoint by adjust_comfort_offset
                
    if TSetMax_baseline == Tlimit_max:
        TSetMax = TSetMax_baseline # Keep maximum setpoint
    else: 
        TSetMax = TSetMax_baseline + adjust_comfort_offset # Adjust maximum setpoint by adjust_comfort_offset

    return  TSetMin, TSetMax
