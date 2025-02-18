def shift_price_occ_event (schedule_price, schedule_occupancy, price_threshold_value, occ_min_threshold, shift_horizon_time):

    '''Define whether to compute DF shift control or not.
    
        Parameters
        ----------
        schedule_price : int or float
            Contains the scheduled price value.

        schedule_occupancy : int or float
            Contains the scheduled occupancy value.

        price_threshold_value : int
            Contains the price threshold value that activates a DR event.

        occ_min_threshold : int
            Contains the minimum occupancy value detected in the schedule list.

        shift_horizon_time : int
            Contains start time of the shift period. Multiply hours by 4 for 15-minute intervals, by 2 for 30-minute intervals, etc.
    
        Returns
        -------
        compute_shift : boolean
            Contains a value to define whether to compute DF shift control or not.
    
        '''
    # activation step means that price[i] > price_threshold and occ[i] > occ_min_threshold
    # if anytime before an activation step within the shift horizon there is no occ while there is high price, does not active shift
    # otherwise, it leads to demand spikes wihtout need  
    def check_future_condition(price, occ, price_threshold_value, occ_min_threshold):
        for i in range(len(price)):
            # Check if both price and occ are greater than their thresholds
            if price[i] > price_threshold_value and occ[i] > occ_min_threshold:
                # Check if all the previous elements of occ are less than or equal to min and price is greater than its threshold 
                for j in range(i):
                    if occ[j] <= occ_min_threshold and price[j] > price_threshold_value:
                        return False
                # If no previous element violates the condition, return True
                return True
        # If no element satisfies the condition, return False
        return False

    for i in range(shift_horizon_time):

        current_condition = schedule_price[i] < price_threshold_value
        future_hours_conditions = check_future_condition(schedule_price[i:i+shift_horizon_time], schedule_occupancy[i:i+shift_horizon_time], price_threshold_value, occ_min_threshold)

        print("future_occ_schedule", schedule_occupancy[i:i+shift_horizon_time])
        print("future_price", schedule_price[i:i+shift_horizon_time])
        
        print('shift event', current_condition and future_hours_conditions)
        
        if current_condition and future_hours_conditions:
                compute_shift = True
        else:
            compute_shift = False
    
        return compute_shift
    