def qualify_zones (operation_mode, zone_temp,  schedule_occupancy, occ_min_threshold, occ_flex_set_temp_min, occ_flex_set_temp_max, non_occ_flex_set_temp_min, non_occ_flex_set_temp_max,
                    hands_off_zone, zone_name, zone_set_temp_heat, zone_set_temp_cool, vav_damper_set, vav_discharge_temp, vav_reheat_command, ahu_supply_temp, ahu_supply_flow, ahu_supply_flow_set): 
             
    '''Define whether to qualify the zone to compute DF shed control
    
        Parameters
        ----------
        operation_mode : str
            Contains the value of the current iteration for the operation mode.

        zone_temp : int or float
            Contains the value of the current iteration for the zone temperature measurement. 

        occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during occupancy.

        occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during occupancy.

        non_occ_flex_set_temp_min : int or float
            Contains the minimum setpoint value for temperature allowed for DF during non-occupancy.

        non_occ_flex_set_temp_max : int or float
            Contains the maximum setpoint value for temperature allowed for DF during non-occupancy.

        hands_off_zone: list
            Contains the names of specific zones explicitly designated to be excluded from DR control.

        zone_name: str
            Contains the name of the zone of the current iteration.

        zone_set_temp_heat : int or float
            Contains the value of the current iteration for the zone heating temperature setpoint measurement.

        zone_set_temp_cool : int or float
            Contains the value of the current iteration for the zone cooling temperature setpoint measurement. 

        vav_damper_set
            Contains the value of the current iteration for the VAV damper setpoint.

        vav_discharge_temp : int or float
            Contains the value of the current iteration for the discharge air temperature of the VAV terminal unit.

        vav_reheat_command : float
            Contains the value of the current iteration for the reheat VAV valve command / control signal.

        ahu_supply_temp : int or float
            Contains the value of the current iteration for the supply air temperature of the air handling unit (AHU).

        ahu_supply_flow : int or float
            Contains the value of the current iteration for the VAV airflow measurement.

        Ahu_flowSupSet : int or float
            Contains the value of the current iteration for the VAV airflow setpoint.

        Returns
        -------
        qualify : boolean
            Contains a value to define whether to qualify the zone to compute DF control.

        '''   
    #Check current Min and Max setpoints
    if schedule_occupancy[0] > occ_min_threshold:
        TSetMin = occ_flex_set_temp_min
        TSetMax = occ_flex_set_temp_max
    else:
        TSetMin = non_occ_flex_set_temp_min 
        TSetMax = non_occ_flex_set_temp_max    
    
    #Out of comfort
    qualify = False
    if TSetMin < zone_temp < TSetMax:
        qualify = True   
    else:
        qualify = False

    if qualify == False:
        print("out-of-comfort zone")
        return qualify
    
    #Hands-off zone
    elif zone_name not in hands_off_zone:
        qualify = True
    else:
        qualify = False

    if qualify == False:
        print("hands-off zone") 
        return qualify

    #Starved zone
    elif vav_damper_set is None: 
        qualify = True
        #print("cannot verify damper position for starved zone")
    elif vav_damper_set > 1:
        qualify = False
    else:
        qualify = True

    if qualify == False:
        print("starved zone")
        return qualify

    #Rogue zone
    elif zone_set_temp_cool is None: 
        qualify = True 
        #print("cannot verify TSetCooZon value for rogue zone")
    elif zone_set_temp_cool < 22.2 + 273.15:
        qualify = False                     
    else:
        qualify = True

    if qualify == False:
        print("rogue zone: cooling setpoint too low", zone_set_temp_cool)
        return qualify
    
    elif zone_set_temp_heat is None: 
        qualify = True 
        #print("cannot verify TSetHeaZon value for rogue zone")
    elif zone_set_temp_heat > 27.8 + 273.15:
        qualify = False                     
    else:
        qualify = True

    if qualify == False:
        print("rogue zone: heating setpoint too high", zone_set_temp_heat)
        return qualify

    elif operation_mode == 'heat':
        if vav_discharge_temp is None: 
            qualify = True 
            #print("cannot verify low discharge temperature for rogue zone")
        elif vav_reheat_command is None: 
            qualify = True 
            #print("cannot verify low discharge temperature for rogue zone")
        elif vav_discharge_temp < 23.9 + 273.15 and vav_reheat_command >= 0.90: 
            qualify = False 
        else:
            qualify = True

    if qualify == False:
        print("rogue zone: low discharge temperature")
        return qualify

    elif operation_mode == 'cool':
        if vav_discharge_temp is None: 
            qualify = True 
            #print("cannot verify leaky reheat value for rogue zone")    
        elif ahu_supply_temp is None: 
            qualify = True 
            #print("cannot verify leaky reheat value for rogue zone")
        elif vav_discharge_temp > ahu_supply_temp + 2.8 and vav_reheat_command == 0: 
            qualify = False                     
        else:
            qualify = True

    if qualify == False:
        print("rogue zone: leaky reheat valve")
        return qualify

    elif ahu_supply_flow is None: 
        qualify = True 
        #print("cannot verify supply air flow setpoint for rogue zone")
    elif ahu_supply_flow_set is None: 
        qualify = True 
        #print("cannot verify supply air flow setpoint for rogue zone")
    elif (ahu_supply_flow < ahu_supply_flow_set*0.9 or ahu_supply_flow > ahu_supply_flow_set*1.1) and (ahu_supply_flow_set - ahu_supply_flow) > 1.4/60:
        qualify = False                     
    else:
        qualify = True

    if qualify == False:
        print("rogue zone: supply air flow setpoint not met")

    return qualify
    