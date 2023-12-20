def shed_price_event (current_price, price_threshold_value):

    '''Define whether to compute DR shed control or not.
    
        Parameters
        ----------
        current_price : int 
            Contains the value of the current iteration for the price schedule. 

        price_threshold_value : int
            Contains the price threshold value that activates a DR event.
       
        Returns
        -------
        compute_shed : boolean
            Contains a value to define whether to compute DR shed control or not.
    
        '''
    if current_price >= price_threshold_value:
        compute_shed = True              
        return compute_shed  
    else:
        compute_shed = False
        return compute_shed



