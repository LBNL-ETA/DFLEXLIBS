def shift_occ_price_event (current_price, future_price, future_occ_schedule, price_threshold_value, 
                           occ_min_threshold, start_time_days, TZon, future_TSetMax_baseline, future_TSetMin_baseline):

    '''Define whether to compute DR shift control or not.
    
        Parameters
        ----------
        current_price : int 
            Contains the value of the current iteration for the price schedule. 
        
        future_price : int 
            Contains the value of the future iteration for the price schedule. 

        future_occ_schedule : int 
            Contains the value of the future iteration for the occupancy schedule. 

        price_threshold_value : int
            Contains the price threshold value that activates a DR event.

        occ_min_threshold : int
            Contains the minimum occupancy value detected in the schedule list.

        start_time_days : int
            Contains start time of the test period in days.

        TZon : int
            Contains the value of the current iteration for the zone temperature measurement. 

        future_TSetMin_baseline: int 
            Contains the future iteration for the temperature limit minimum that allows the HVAC system to operate.

        future_TSetMax_baseline: int 
            Contains the future iteration for the temperature limit minimum that allows the HVAC system to operate.      
            
        Returns
        -------
        compute_shift : boolean
            Contains a value to define whether to compute DR shift control or not.
    
        '''
    print("current_price", current_price, "price_threshold_value", price_threshold_value, "future_price", future_price, "future_occ_schedule", future_occ_schedule)
    print(current_price < price_threshold_value, future_price >= price_threshold_value, future_occ_schedule > occ_min_threshold)
    if current_price < price_threshold_value and future_price >= price_threshold_value and future_occ_schedule > occ_min_threshold:
        # Check the HVAC operation (heating/cooling) mode based on season
        # Assuming heating season to be the period from October through April.
        if start_time_days < 120 or start_time_days > 273: 
            print("heating season")
            # Check for current temperature status to verify if shift is feasible  
            print(TZon < future_TSetMax_baseline)
            if TZon < future_TSetMax_baseline:    
                compute_shift = True
        else:
            print("cooling season")
            # Check for current temperature status to verify if shift is feasible  
            print(TZon > future_TSetMin_baseline)
            if TZon > future_TSetMin_baseline:    
                compute_shift = True

        return compute_shift  
    else:
        compute_shift = False
        return compute_shift
    