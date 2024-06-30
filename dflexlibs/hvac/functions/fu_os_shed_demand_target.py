def shed_demand_target (demand_decrease_cap, demand_decrease, demand_decrease_error, demand_decrease_error_min):

    '''Define .

        Parameters
        ----------            
        
        demand_decrease_cap : int or float
            Contains the objective demand decrease.

        demand_decrease : int or float
            Contains the current demand decrease value.

        demand_decrease_error : int or float
            Contains the difference between DDcap and current building demand.

        demand_decrease_error_min : int or float
            Contains the minimum allowable difference between DDcap and current building demand.
            
        Returns
        -------

        target_met : boolean
            Contains a value to define whether to the demand target has been met.


    '''    
    demand_decrease_error = demand_decrease_cap - demand_decrease 
    
    if  demand_decrease_error > demand_decrease_error_min:
        target_met = True
    else:
        target_met = False

    return target_met