def compute_control(zone_set_temp_heat, zone_set_temp_cool,zone_set_temp_heat_name, zone_set_temp_cool_name, 
zone_set_temp_heat_bas_schedule, zone_set_temp_cool_bas_schedule):
 
    ''' Compute a rule based control for testing a baseline scenario.

        Parameters
        ----------            

        Returns
        -------


    '''    
    control_results = {}  

    # Compute baseline temperature sepoints
    if zone_set_temp_heat is not None:
        control_results [zone_set_temp_heat_name] = zone_set_temp_heat_bas_schedule[0]
    if zone_set_temp_cool is not None:
        control_results [zone_set_temp_cool_name] = zone_set_temp_cool_bas_schedule[0] 
    
    return control_results

def sparql_query(graph_path, query_paths):

    '''Query identifiers for control points per zone from the selected graph path.

        Parameters
        ----------            

        graph_path : str
            Contains the path to the graph directory.
        
        query_paths : str
            Contains the paths to the sparql queries.

        Returns
        -------


    '''    

    from rdflib.plugins.sparql import prepareQuery
    import rdflib
    from rdflib import Namespace
    
    # Query the identifiers for control points per zone    
    g = rdflib.Graph()
    g.parse(graph_path)

    # Create lists for the identifiers needed to instatiate the required data points 
    zone_set_temp_point = []
    zone_set_temp_heat_point = []
    zone_set_temp_cool_point = []
    zone_names = []
    unocc_zone_set_temp_heat_point = []
    unocc_zone_set_temp_cool_point = []
    occ_zone_set_temp_heat_point = []
    occ_zone_set_temp_cool_point = []
    occ_sensor_point  = []    
    occ_cmd_point  = []    

    
    # Iterate over the query paths and execute each query
    for query_path in query_paths:
        with open(query_path) as f:
            query_text = f.read()
        
        # Execute the query
        qres = g.query(query_text)

        # Process the results
        for row in qres:
            print(str(row))
            

            zone_set_temp_point_value = getattr(row, 'zone_set_temp_point', None)

            zone_set_temp_heat_point_value = getattr(row, 'zone_set_temp_heat_point', None)
            zone_set_temp_cool_point_value = getattr(row, 'zone_set_temp_cool_point', None)

            zone_names_value = getattr(row, 'zone_name', None)

            unocc_zone_set_temp_heat_point_value = getattr(row, 'unocc_zone_set_temp_heat_point', None)
            unocc_zone_set_temp_cool_point_value = getattr(row, 'unocc_zone_set_temp_cool_point', None)

            occ_zone_set_temp_heat_point_value = getattr(row, 'occ_zone_set_temp_heat_point', None)
            occ_zone_set_temp_cool_point_value = getattr(row, 'occ_zone_set_temp_cool_point', None)

            occ_sensor_point_value = getattr(row, 'occ_sensor_point', None)
            occ_cmd_point_value = getattr(row, 'occ_cmd_point', None)

            if zone_set_temp_point_value is not None:
                zone_set_temp_point.append(str(zone_set_temp_point_value))
            
            if zone_set_temp_heat_point_value is not None:
                zone_set_temp_heat_point.append(str(zone_set_temp_heat_point_value))
            if zone_set_temp_cool_point_value is not None:
                zone_set_temp_cool_point.append(str(zone_set_temp_cool_point_value))

            if zone_names_value is not None:
                zone_names.append(str(zone_names_value))

            if unocc_zone_set_temp_heat_point_value is not None:
                unocc_zone_set_temp_heat_point.append(str(unocc_zone_set_temp_heat_point_value))
            if unocc_zone_set_temp_cool_point_value is not None:
                unocc_zone_set_temp_cool_point.append(str(unocc_zone_set_temp_cool_point_value))

            if occ_zone_set_temp_heat_point_value is not None:
                occ_zone_set_temp_heat_point.append(str(occ_zone_set_temp_heat_point_value))
            if occ_zone_set_temp_cool_point_value is not None:
                occ_zone_set_temp_cool_point.append(str(occ_zone_set_temp_cool_point_value))

            if occ_sensor_point_value is not None:
                occ_sensor_point.append(str(occ_sensor_point_value))

            if occ_cmd_point_value is not None:
                occ_cmd_point.append(str(occ_cmd_point_value))


    number_of_zones = range(len(zone_names))
    return number_of_zones, zone_names, zone_set_temp_point, zone_set_temp_heat_point, zone_set_temp_cool_point, unocc_zone_set_temp_heat_point, unocc_zone_set_temp_cool_point, occ_zone_set_temp_heat_point, occ_zone_set_temp_cool_point, occ_sensor_point, occ_cmd_point

