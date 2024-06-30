def shift_check_demand(baseline_demand_peak, current_demand, peak_demand_diff_error_min, deadband_peak_demand_diff_error_min):

'''Check if current demand requires modulation.
    
        Parameters
        ----------
    
       baseline_demand_peak : int or float
            Contains baseline demand peak value across the simulated period.

        current_demand : int or float
            Contains the current demand value.
        
        peak_demand_diff_error_min : int or float
            Contains the predefined minimum peak demand difference error.
        
        deadband_peak_demand_diff_error_min: int or float
            Contains the predefined minimum deadband peak peak demand difference error.
    
    Returns
        -------
        qualify : boolean
            Contains a value to define whether to building requires activation of demand modulation.

        '''  
    peak_demand_diff = baseline_demand_peak - current_demand
    
    if peak_demand_diff < peak_demand_diff_error_min + deadband_peak_demand_diff_error_min:
        reduce_VAV = 1
        print(reduce_VAV)
    else:
        reduce_VAV = 0

    return reduce_VAV