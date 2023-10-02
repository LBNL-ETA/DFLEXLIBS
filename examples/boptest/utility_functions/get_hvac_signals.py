### Function to define HVAC heat_signal and cool_signal which varies between test cases ###

#################################
# bestest_air #

def get_bestest_air_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, heat_signal, cool_signal):
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
    
    updated_heat_signal = heat_signal
    updated_cool_signal = cool_signal
    updated_TSetHeaZonPoint = None
    updated_TSetCooZonPoint = None
    
    # Get supply air temperature setpoint to define if in heating mode (according to https://ibpsa.github.io/project1-boptest/docs-testcases/bestest_air/index.html)
    if y[hvac_mode_identifier] >= 298.15 and y[hvac_mode_identifier] <= 313.15: # 24 to 40
        updated_heat_signal = 1
        updated_cool_signal = 0

    # Get supply air temperature setpoint to define if in cooling mode (according to https://ibpsa.github.io/project1-boptest/docs-testcases/bestest_air/index.html)
    elif y[hvac_mode_identifier] >= 285.15 and y[hvac_mode_identifier] < 298.15: # 12 to 24
        updated_cool_signal = 1
        updated_heat_signal = 0
        
    if TSetHeaZonPoint == 'N/A':
        updated_TSetHeaZonPoint = TSetZonPoint
    else:
        updated_TSetHeaZonPoint = TSetHeaZonPoint
    
    if TSetCooZonPoint == 'N/A':
        updated_TSetCooZonPoint = TSetZonPoint
    else:
        updated_TSetCooZonPoint = TSetCooZonPoint
    print(updated_heat_signal, updated_cool_signal, y[hvac_mode_identifier])
    return updated_heat_signal, updated_cool_signal, updated_TSetHeaZonPoint, updated_TSetCooZonPoint

#################################
# bestest_hydronic_heat_pump #

def get_hydronic_hp_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, heat_signal, cool_signal):
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
            Contains updated heating signal to define the HVAC operation mode.

        updated_cool_signal : int
            Contains updated cooling signal to define the HVAC operation mode.

        updated_TSetHeaZonPoint : int
            Contains the updated value of the current iteration for the zone heating temperature setpoint measurement. 

        updated_TSetCooZonPoint : int
            Contains the updated value of the current iteration for the zone cooling temperature setpoint measurement. 

'''
    
    updated_heat_signal = heat_signal
    updated_cool_signal = cool_signal
    updated_TSetHeaZonPoint = None
    updated_TSetCooZonPoint = None

    # Get heat pump modulating signal for compressor speed between 0 (not working) and 1 (working at maximum capacity) (according to https://ibpsa.github.io/project1-boptest/docs-testcases/bestest_hydronic_heat_pump/index.html)
    if y[hvac_mode_identifier] > 0.5:
        
        updated_heat_signal = 1
        updated_cool_signal = 0
    
    if TSetHeaZonPoint == ['N/A']:
        updated_TSetHeaZonPoint = TSetZonPoint
    else:
        updated_TSetHeaZonPoint = TSetHeaZonPoint 
    
    return updated_heat_signal, updated_cool_signal, updated_TSetHeaZonPoint, updated_TSetCooZonPoint

#################################
# multizone_office_simple_air #

def get_multizone_office_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, heat_signal, cool_signal):
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
    
    updated_heat_signal = heat_signal
    updated_cool_signal = cool_signal
    updated_TSetHeaZonPoint = None
    updated_TSetCooZonPoint = None
    
    # Get heating coil pump control signal for AHU to define if in heating mode
    if y[heat_signal_identifier] >= 0.5:
        updated_heat_signal = y[heat_signal_identifier]
        updated_cool_signal = 0
        

    # Get cooling coil pump control signal for AHU to define if in cooling mode
    elif y[cool_signal_identifier] >= 0.5:
        updated_cool_signal = y[cool_signal_identifier]
        updated_heat_signal = 0
        
    if TSetHeaZonPoint == 'N/A':
        updated_TSetHeaZonPoint = TSetZonPoint
    else:
        updated_TSetHeaZonPoint = TSetHeaZonPoint

    if TSetCooZonPoint == 'N/A':
        updated_TSetCooZonPoint = TSetZonPoint
    else:
        updated_TSetCooZonPoint = TSetCooZonPoint
    
    return updated_heat_signal, updated_cool_signal, updated_TSetHeaZonPoint, updated_TSetCooZonPoint

#################################
# singlezone_commercial_hydronic #

def get_singlezone_commercial_hvac_signals(y, hvac_mode_identifier, heat_signal_identifier, cool_signal_identifier, TSetZonPoint, TSetHeaZonPoint, TSetCooZonPoint, heat_signal, cool_signal):
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
    
    updated_heat_signal = heat_signal
    updated_cool_signal = cool_signal
    updated_TSetHeaZonPoint = None
    updated_TSetCooZonPoint = None

    # Get pump speed control signal for heating distribution system (according to https://ibpsa.github.io/project1-boptest/docs-testcases/singlezone_commercial_hydronic/index.html)
    if y[hvac_mode_identifier] > 0.5:
        updated_heat_signal = 1
        updated_cool_signal = 0
    
    if TSetHeaZonPoint == ['N/A']:
        updated_TSetHeaZonPoint = TSetZonPoint
    else:
        updated_TSetHeaZonPoint = TSetHeaZonPoint 
    
    return updated_heat_signal, updated_cool_signal, updated_TSetHeaZonPoint, updated_TSetCooZonPoint

