from collections import OrderedDict

def organize_units(unit_dict):
    """
    Takes dictionary of units, organizes them first by Deta T and based on inactive period 
    
    params
    --
    unit_dict: dict
    {unit_id: delta_t: val, temp: val, inactive_period: val}, unit_id2: {delta_t: val, inactive_period: val} }

    returns 
    ordered_dict: dict
    ordered dictionary of units from least delta t and time inactive to most delta_t and time inactive (i.e. later units are activated)
    
    """
    sorted_dict = sorted(unit_dict.items(), key=lambda x: (x[1]['delta_t'], x[1]['inactive_period']), reverse = True)


    return OrderedDict(sorted_dict)

def get_active_units(unit_dict, active_unit_count):
    """
    Take the orderd unit dict and return a new dictionary indicating 
    which units should be active and which should not be
    """
    i = 0
    organized_unit_dict = organize_units(unit_dict)

    for k in organized_unit_dict.keys():
        is_active = i < active_unit_count
        unit_dict[k]['active'] = is_active
        i += 1
    print(unit_dict)
    return unit_dict

def TSetHeaZon_TSetCooZon_stagger(active_units, min_sp, max_sp):
    """
    The set setpoints function is different based on the configuration of the building
    This is especially true of setpoint configurations

    If it has cooling and heating setpoint then we can widen the deadband by writing them independently
    If it has a mode, the mode can be written and the relevant setpoint
    This can be done with different "set setpoints" functions, or with adapter functions that 
    work on its output

    Can be used as on-off controls if desired. However setpoints are a more readily available point

    """    
    setpoint_df = {}

    for k, v in active_units.items():        
        if not v['active']:
            v['TSetCooZon'] = max_sp 
            v['TSetHeaZon'] = min_sp 
    return active_units

def set_setpoints_setpoint_and_mode(active_units, unit_dict, min_sp, max_sp, mode):
    """
    Adjusts the output of the set_setpoints function for units with a single setpoint and a defined mode
    requires knowledge of the current heating mode (if it's heating or cooling)
    """
    setpoint_df = {}
    for k, v, in active_units.items():        
        if v:
            if mode == 'heat':
                setpoint_df[k]['setpoint'] = min_sp
            if mode == 'cool':
                setpoint_df[k]['setpoint'] = max_sp
            if mode == 'auto':
                print('mode must be writable for this')
                setpoint_df[k]['setpoint'] = min_sp
                setpoint_df[k]['mode'] = 'heat'

            
        else:
            setpoint_df[k]['setpoint'] = None

def get_delta_t(TZon, TSetCooZon, TSetHeaZon):
    # function to be improved. 
    # Should this eliminate simultaneous heating and cooling? Separate application? 
    # need a version that works for mode and single setpoint 
    """
    delta T is how far out of deadband the point is. 
    If the point is within the deadband, it is whichever of heating or cooling the zone temp is closer too
    for now making delta T 0 if it is within the deadband. 
    """
    if TSetCooZon > TZon: 
        delta_t = TSetCooZon - TZon
    elif TSetHeaZon < TZon: 
        delta_t = TZon - TSetHeaZon
    else:
        delta_t = 0 
    return delta_t 

def get_inactive_period(active_step, step):
    # TODO
    pass