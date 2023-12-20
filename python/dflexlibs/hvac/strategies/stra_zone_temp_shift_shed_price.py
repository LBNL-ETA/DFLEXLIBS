import rdflib
# a lot of the parameters of this function could be provided by the Interface class if we want
# Update: I tried providing the class and I think it doesn't make sense
# The control strategies motivate the creation of the interface class as well as the control functions class.
# Having each function and variable separately documented in this function makes usage of the library MUCH more clear. 
# Control strategies are what you want to run, you assemble everything else based on the strategy. 

def compute_control(setpoint_adjustment, runaway_condition, heat_runaway, cool_runaway, shift_occ_price_event, shed_price_event, heat_shift, cool_shift, heat_shed, cool_shed, 
                    new_comfort_range, step, TZon, TSetMin_baseline, TSetMax_baseline, TSetHeaZon, TSetCooZon, Tlimit_min, 
                    Tlimit_max, current_price, future_price, price_threshold_value, current_occ_status, current_occ_schedule, 
                    future_occ_schedule, occ_min_threshold, adj_comfort_range_flag, adj_comfort_range_value, heat_signal, cool_signal, TSetHeaZon_name, 
                    TSetCooZon_name, start_time_days, future_TSetMin_baseline, future_TSetMax_baseline):
 
    '''Compute the control output based on measurement and forecast values.
    
        Parameters
        ----------
        setpoint_adjustment : function
            Function used to determine the amount setpoints should be adjusted by step.

        runaway_condition : function 
            Function used to identify if there is thermal runaway.

        heat_runaway : function 
            Function used to correct thermal runaway for heating.

        cool_runaway : function 
            Function used to correct thermal runaway for cooling.            
            
        shift_occ_price_event : function 
            Function used to identify if DR shift control must be executed based on price and occupancy event.

        shed_price_event : function 
            Function used to identify if DR shed control must be executed based on price event.
            
        heat_shift : function
            Function used to determine the change in heating setpoint during load shifting.

        cool_shift : function 
            Function used to determine the change in cooling setpoint during load shifting.
           
        heat_shed : function
            Function used to determine the change in heating setpoint during load shedding.

        cool_shed : function 
            Function used to determine the change in cooling setpoint during load shedding.
           
        new_comfort_range : function 
            Function used to determine the new comfort range when adjust_comfort_range is True.

        step : int
            Contains the current step value.

        TZon : int
            Contains the value of the current iteration for the zone temperature measurement. 

        TSetMin_baseline : int 
            Contains the value of the current iteration for the minimum temperature of the baseline comfort range.

        TSetMax_baseline : int 
            Contains the value of the current iteration for the maximum temperature of the baseline comfort range.

        TSetHeaZon : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSetCooZon : int
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        Tlimit_min : int
            Contains the temperature limit minimum that allows the HVAC system to operate.

        Tlimit_max : int
            Contains the temperature limit maximum that allows the HVAC system to operate.

        current_price : int 
            Contains the value of the current iteration for the price schedule. 

        future_price : int 
            Contains the value of the future iteration for the price schedule. 

        price_threshold_value : int
            Contains the price threshold value that activates a DR event.
            
        current_occ_status : int 
            Contains the value of the future iteration for the occupancy status. 

        current_occ_schedule : int 
            Contains the value of the future iteration for the occupancy schedule. 

        future_occ_schedule : int 
            Contains the value of the future iteration for the occupancy schedule. 

        occ_min_threshold : int
            Contains the minimum occupancy value detected in the schedule list.

        adj_comfort_range_flag : boolean
            Contains flag to define if comfort range adjustment is needed. 

        adj_comfort_range_value : int
            Contains allowed increase and decrease temperature value (offset) from baseline comfort range.

        heat_signal : int
            Contains heating signal to define the HVAC operation mode.

        cool_signal : int
            Contains cooling signal to define the HVAC operation mode.

        TSetHeaZon_name : str
            Contains the name of the zone temperature heating setpoint.

        TSetCooZon_name : str
            Contains the name of the zone temperature cooling setpoint.

        start_time_days : int
            Contains start time of the test period in days.

        future_TSetMin_baseline: int 
            Contains the future iteration for the temperature limit minimum that allows the HVAC system to operate.

        future_TSetMax_baseline: int 
            Contains the future iteration for the temperature limit minimum that allows the HVAC system to operate.

        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
       
    control_results = {}

    # Change comfort range for DR conditions if defined as True in the config file  
    if adj_comfort_range_flag is True and shed_price_event(current_price, price_threshold_value):
        TSetMin, TSetMax = new_comfort_range (TSetMin_baseline, TSetMax_baseline, Tlimit_min, Tlimit_max, adj_comfort_range_value)
    else:
        TSetMin = TSetMin_baseline 
        TSetMax = TSetMax_baseline 
    print("TSetMin_baseline", TSetMin_baseline, "TSetMin", TSetMin)
    print("TSetMax_baseline", TSetMax_baseline, "TSetMax", TSetMax)

    # Call ashrae_TSet_adjust function to define temperatue adjustment value
    TSet_adj_current = setpoint_adjustment(step)
    
    if runaway_condition (TZon, TSetMin, TSetMax):
        # Check the HVAC operation (heating/cooling) mode
        if heat_signal >= 0.5 and cool_signal == 0:   
            if TSetHeaZon is not None:
                # Call runaway correction to adjust the zone heating temperature setpoint                
                new_TsetHeaZon = heat_runaway(TSetMin_baseline, TSetHeaZon, TSet_adj_current)
                enabled_command = 1             
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
                control_results [TSetHeaZon_name] = new_TsetHeaZon
            
            if TSetCooZon is not None:
                control_results [TSetCooZon_name] = TSetMax_baseline
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            print("runaway condition", control_results) 

        elif cool_signal >= 0.5 and heat_signal == 0:
            if TSetCooZon is not None:
                # Call runaway correction to adjust the zone cooling temperature setpoint                
                new_TsetCooZon = cool_runaway(TSetMax_baseline, TSetCooZon, TSet_adj_current)                
                control_results [TSetCooZon_name] = new_TsetCooZon
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            
            if TSetHeaZon is not None:
                control_results [TSetHeaZon_name] =  TSetMin_baseline
                enabled_command = 1             
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
            print("runaway condition", control_results) 
        return control_results

    # Call shift function
    print("call shift")
    if shift_occ_price_event(current_price, future_price, future_occ_schedule, price_threshold_value, occ_min_threshold, 
                             start_time_days, TZon, future_TSetMax_baseline, future_TSetMin_baseline):
        print("enter shift")
            # Check the HVAC operation (heating/cooling) mode based on season
            # Assuming heating season to be the period from October through April.
        if start_time_days < 120 or start_time_days > 273: 
            if TSetHeaZon is not None:
                # Call shift_TsetHeaZon function        
                new_TsetHeaZon = heat_shift(TSetHeaZon, TSet_adj_current, future_TSetMin_baseline)
                control_results [TSetHeaZon_name] = new_TsetHeaZon
                enabled_command = 1
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
            
            if TSetCooZon is not None:
                # Release DR control (compute baseline max temperature sepoints)
                control_results [TSetCooZon_name] = TSetMax_baseline
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            print("shift heat", control_results) 

        else:
            if TSetCooZon is not None:
                # Call shift_TsetCooZon function
                new_TsetCooZon = cool_shift (TSetCooZon, TSet_adj_current, future_TSetMax_baseline)
                control_results [TSetCooZon_name] = new_TsetCooZon
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            
            if TSetHeaZon is not None:
                # Release DR control (compute baseline min temperature sepoints)
                control_results [TSetHeaZon_name] =  TSetMin_baseline
                enabled_command = 1           
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
            print("shift cool", control_results) 
        
    # Call shed function
    elif shed_price_event(current_price, price_threshold_value):
        # Check the HVAC operation (heating/cooling) mode
        if heat_signal >= 0.5 and cool_signal == 0 or (heat_signal < 0.5 and cool_signal == 0 and (start_time_days < 120 or start_time_days > 273)):  
            if TSetHeaZon is not None:
                # Call shed_TsetHeaZon function        
                new_TsetHeaZon = heat_shed (TSetHeaZon, TSet_adj_current, TSetMin, current_occ_status, current_occ_schedule, occ_min_threshold)
                control_results [TSetHeaZon_name] = new_TsetHeaZon
                enabled_command = 1
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
                
            if TSetCooZon is not None:
                # Release DR control (compute baseline max temperature sepoints)
                control_results [TSetCooZon_name] = TSetMax_baseline
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            print("shed heat", control_results)

        else:
            if TSetCooZon is not None:
                # Call shed_TsetCooZon function
                new_TsetCooZon = cool_shed (TSetCooZon, TSet_adj_current, TSetMax, current_occ_status, current_occ_schedule, occ_min_threshold)
                control_results [TSetCooZon_name] = new_TsetCooZon
                enabled_command = 1
                control_results [TSetCooZon_name + '_enable'] =  enabled_command
            
            if TSetHeaZon is not None:
                # Release DR control (compute baseline min temperature sepoints)
                control_results [TSetHeaZon_name] =  TSetMin_baseline
                enabled_command = 1             
                control_results [TSetHeaZon_name + '_enable'] =  enabled_command
            print("shed cool", control_results)            
                
    else:
        if TSetHeaZon is not None:
            # Release DR control (compute baseline min temperature sepoints)
            control_results [TSetHeaZon_name] =  TSetMin_baseline
            enabled_command = 1            
            control_results [TSetHeaZon_name + '_enable'] =  enabled_command
            
        if TSetCooZon is not None:
            # Release DR control (compute baseline max temperature sepoints)
            control_results [TSetCooZon_name] = TSetMax_baseline
            enabled_command = 1
            control_results [TSetCooZon_name + '_enable'] =  enabled_command
        print("release DR", control_results)    
  
    print(control_results)
    return control_results
                                             
def sparql_query(graph_path, query_path):

    '''Query identifiers for control points per zone from the selected graph path.

        Parameters
        ----------            

        graph_path : str
            Contains the path to the graph directory.
        
        query_path : str
            Contains the path to the sparql query.

        Returns
        -------

        range_query : int
            Contains the length of the query results, ie the number of zones with sufficient points from the graph. 

        TZonPoint : str
            Contains the identifier for the temperature measurement point per zone. 

        TSetZonPoint : str
            Contains the identifier for the temperature setpoint per zone.

        TSetHeaZonPoint : str
            Contains the identifier for the heating temperature setpoint per zone. 

        TSetCooZonPoint : str
            Contains the identifier for the cooling temperature setpoint per zone. 

        TSetMinPoint : str
            Contains the identifier for the minimum temperature setpoint per zone.

        TSetMaxPoint : str
            Contains the identifier for the maximum temperature setpoint per zone.

        occSensorPoint : str
            Contains the identifier for the occupancy sensor per zone.

    '''    

    # Query the identifiers for control points per zone    
    g = rdflib.Graph()
    g.parse(graph_path)
    with open(query_path) as f:
        query = f.read()
    qres = g.query(query)
    range_query = range(len(qres))

    # Create lists for the identifiers needed to instatiate the control points per zone
    TZonPoint = []
    TSetZonPoint = []
    TSetHeaZonPoint = []
    TSetCooZonPoint = []
    TSetMinPoint = []
    TSetMaxPoint  = []
    occSensorPoint  = []

    for row in qres:
        TZonPoint.append (str(row.TZonPoint))
        TSetZonPoint.append (str(row.TSetZonPoint))
        TSetHeaZonPoint.append (str(row.TSetHeaZonPoint))
        TSetCooZonPoint.append (str(row.TSetCooZonPoint))
        TSetMinPoint.append (str(row.TSetMinPoint))
        TSetMaxPoint .append (str(row.TSetMaxPoint ))
        occSensorPoint .append (str(row.occSensorPoint ))

    return range_query, TZonPoint, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, TSetMinPoint, TSetMaxPoint, occSensorPoint
 