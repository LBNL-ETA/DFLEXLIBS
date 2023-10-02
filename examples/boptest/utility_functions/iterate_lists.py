def iterate_lists_zone_temp_shift_shed_price (TSetMin_baseline_schedule, TSetMax_baseline_schedule, occupancy_schedule,
                occupancy_status, price_schedule, shift_horizon_time):
    for i in range(len(TSetMin_baseline_schedule)):
        current_TSetMin_baseline = TSetMin_baseline_schedule[i]
        current_TSetMax_baseline = TSetMax_baseline_schedule[i]
        current_occ_schedule = occupancy_schedule[i]
        current_occ_status = occupancy_status[i]
        current_price = price_schedule[i]   
               
        future_price = price_schedule[i+shift_horizon_time] # shift_horizon time ahead
        future_occ_schedule = occupancy_schedule[i+shift_horizon_time] # shift_horizon time ahead
        future_TSetMin_baseline = TSetMin_baseline_schedule[i+shift_horizon_time] # shift_horizon time ahead
        future_TSetMax_baseline = TSetMax_baseline_schedule[i+shift_horizon_time] # shift_horizon time ahead

        return (current_TSetMin_baseline, current_TSetMax_baseline, current_occ_schedule,
                    current_occ_status, current_price, future_price, future_occ_schedule, 
                    future_TSetMin_baseline, future_TSetMax_baseline)

def iterate_lists_zone_temp_shed_price (TSetMin_baseline_schedule, TSetMax_baseline_schedule, occupancy_schedule,
                occupancy_status, price_schedule):
    for i in range(len(TSetMin_baseline_schedule)):
        current_TSetMin_baseline = TSetMin_baseline_schedule[i]
        current_TSetMax_baseline = TSetMax_baseline_schedule[i]
        current_occ_schedule = occupancy_schedule[i]
        current_occ_status = occupancy_status[i]
        current_price = price_schedule[i]   
      
        return (current_TSetMin_baseline, current_TSetMax_baseline, current_occ_schedule,
                    current_occ_status, current_price)
    

           