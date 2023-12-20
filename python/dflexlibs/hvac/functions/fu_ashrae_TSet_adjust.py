def ashrae_TSet_adjust (step):

    '''Define temperature adjusment value allowed for DR operation.

        Parameters
        ----------            
        step : int
            Contains the current step value.

        Returns
        -------

        TSet_adj_current : int
            Contains the current temperature adjusment value allowed for DR operation.

    '''    
    # Compute temperature drift rate allowed under ASHRAE Standard 55 according to time period  
    if step <= 900:         # <= 15 min
        TSet_adj_initial = 1.11
    elif step <= 1800:      # <= 30 min
        TSet_adj_initial = 1.67
    elif step <= 3600:      # <= 60 min
        TSet_adj_initial = 2.22
    else:                   # > 120 min 
        TSet_adj_initial = 2.77

    # Temporary variable to account for ratcheting within the loop (ratcheting logic to be added)
    TSet_adj_current  = TSet_adj_initial

    return TSet_adj_current