### Function to define HVAC heat_signal and cool_signal which varies between test cases ###

#################################
# bestest_air #

def get_bestest_air_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, start_time_days):
    '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
    
    Parameters
    ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        hvac_mode_identifier : str
            Contains naming to identify the HVAC control signal used in this simulation.

        heat_signal_identifier : str
            Contains naming to identify the heating control signal used in this simulation.

        cool_signal_identifier : str
            Contains naming to identify the cooling control signal used in this simulation.


    Returns
    -------
        operation_mode : str
            Contains HVAC operation mode.

'''
    
    # Get supply air temperature setpoint to define if in heating mode (according to https://ibpsa.github.io/project1-boptest/docs-testcases/bestest_air/index.html)
    if start_time_days < 120 or start_time_days > 273 or (294.15 <= y[hvac_mode_identifier] < 313.15): # 21 to 40
        operation_mode = 'heat'
    else:
        operation_mode = 'cool' 
        
    return operation_mode
#################################
# bestest_hydronic_heat_pump #

def get_bestest_hydronic_heat_pump_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, start_time_days):
    '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
    
    Parameters
    ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        hvac_mode_identifier : str
            Contains naming to identify the HVAC control signal used in this simulation.

        heat_signal_identifier : str
            Contains naming to identify the heating control signal used in this simulation.

        cool_signal_identifier : str
            Contains naming to identify the cooling control signal used in this simulation.


    Returns
    -------
        operation_mode : str
            Contains HVAC operation mode.

'''
    
    # Get heat pump modulating signal for compressor speed between 0 (not working) and 1 (working at maximum capacity) (according to https://ibpsa.github.io/project1-boptest/docs-testcases/bestest_hydronic_heat_pump/index.html)
    if start_time_days < 120 or start_time_days > 273 or y[hvac_mode_identifier] > 0.5:
        operation_mode = 'heat'
    else:
        operation_mode = 'cool'
    
    return operation_mode

#################################
# multizone_office_simple_air #

def get_multizone_office_simple_air_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, start_time_days):
    '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
    
    Parameters
    ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        hvac_mode_identifier : str
            Contains naming to identify the HVAC control signal used in this simulation.

        heat_signal_identifier : str
            Contains naming to identify the heating control signal used in this simulation.

        cool_signal_identifier : str
            Contains naming to identify the cooling control signal used in this simulation.


    Returns
    -------
        operation_mode : str
            Contains HVAC operation mode. 

'''
    
   # Get heating coil pump control signal for AHU to define if in heating mode
    if start_time_days < 120 or start_time_days > 273 or (y[heat_signal_identifier] >= 0.5):
        operation_mode = 'heat'
    else:
        operation_mode = 'cool'
    
    return operation_mode

#################################
# singlezone_commercial_hydronic #

def get_singlezone_commercial_hydronic_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, start_time_days):
    '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
    
    Parameters
    ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        hvac_mode_identifier : str
            Contains naming to identify the HVAC control signal used in this simulation.

        heat_signal_identifier : str
            Contains naming to identify the heating control signal used in this simulation.

        cool_signal_identifier : str
            Contains naming to identify the cooling control signal used in this simulation.


    Returns
    -------
        operation_mode : str
            Contains HVAC operation mode.

'''
    
    # Get pump speed control signal for heating distribution system (according to https://ibpsa.github.io/project1-boptest/docs-testcases/singlezone_commercial_hydronic/index.html)
    if start_time_days < 120 or start_time_days > 273 or (y[hvac_mode_identifier] > 0.5):
        operation_mode = 'heat'

    else:
        operation_mode = 'cool'
    
    return operation_mode


#################################
# multizone_residential_hydronic #

def get_multizone_residential_hydronic_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, start_time_days):
    '''Determines the heating and cooling signals for a HVAC system based on the current HVAC mode and zone temperature setpoints.
    
    Parameters
    ----------
        y : dict
            Contains the current values of the measurements.
            {:}

        hvac_mode_identifier : str
            Contains naming to identify the HVAC control signal used in this simulation.

        heat_signal_identifier : str
            Contains naming to identify the heating control signal used in this simulation.

        cool_signal_identifier : str
            Contains naming to identify the cooling control signal used in this simulation.

        TSetZonPoint : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSetHeaZon : int
            Contains the value of the current iteration for the zone heating temperature setpoint measurement. 

        TSetCooZon : int
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        heat_signal : int
            Contains heating signal to define the HVAC operation mode.

        cool_signal : int
            Contains cooling signal to define the HVAC operation mode.    

    Returns
    -------
        updated_heat_signal : int
            Contains heating signal to define the HVAC operation mode.

        updated_cool_signal : int
            Contains cooling signal to define the HVAC operation mode.
 
        updated_TSetHeaZonPoint : int
            Contains the updated value of the current iteration for the zone heating temperature setpoint measurement. 

        updated_TSetCooZonPoint : int
            Contains the updated value of the current iteration for the zone cooling temperature setpoint measurement. 

'''
    
    # Get boiler control signal (according to https://ibpsa.github.io/project1-boptest/docs-testcases/multizone_residential_hydronic/index.html)

    if start_time_days < 120 or start_time_days > 273 or (y[hvac_mode_identifier] >= 0):
        operation_mode = 'heat'

    else:
        operation_mode = 'cool'
    
    return operation_mode #updated_heat_signal, updated_cool_signal, updated_TSetHeaZonPoint, updated_TSetCooZonPoint