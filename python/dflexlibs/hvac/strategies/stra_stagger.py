import rdflib
# a lot of the parameters of this function could be provided by the Interface class if we want
# Update: I tried providing the class and I think it doesn't make sense
# The control strategies motivate the creation of the interface class as well as the control functions class.
# Having each function and variable separately documented in this function makes usage of the library MUCH more clear. 
# Control strategies are what you want to run, you assemble everything else based on the strategy. 

def compute_control(step, unit_dict, get_active_units, 
                    get_setpoints, get_delta_t,
                    active_unit_count, Tlimit_min, Tlimit_max):
 
    '''Compute the control output based on measurement and forecast values.
    
        Parameters
        ----------
        organize_units : function
        
        get_active_units : function
        
        get_inactive_period : function

        get_setpoints : function
        
        get_delta_t : function
        
        step : int
            Contains the current step value.

        active_unit_count: int
            amount of units that should be active at any given time

        Tlimit_min : int
            Contains the temperature limit minimum that allows the HVAC system to operate.

        Tlimit_max : int
            Contains the temperature limit maximum that allows the HVAC system to operate.

        unit_dict: dict
            Dictionary containing the details for each unit. 
                {
                unit_id : str
                    id for a given hvac unit. 

                value : dict
                    dictionary with each units details 
                    {
                    TSetHeaZon: float
                        heating setpoint. If null there is no heating setpoint. 
                    TSetCooZon: float
                        cooling setpoint, can be null if none. 
                    TSetZon: float
                        zone setpoint, can be null if none. 
                    TZon: float
                        Zone temperature for unit 
                    active_step: int
                        last step the point was active .
                        #TODO
                    }                    
                
        Returns
        -------
        control_results : dict
            Defines the control outputs to be used for the next step.
            {:}
    
        '''
       
    control_results = {}

    for unit_id, unit_detail in unit_dict.items():
        unit_detail['delta_t'] = get_delta_t(unit_detail['TZon'], unit_detail['TSetCooZon'], unit_detail['TSetHeaZon'])
        # right now inactive period not implemented 
        # unit_detail['inactive_period'] = get_inactive_period(unit_detail['active_step'], step)
        unit_detail['inactive_period'] = 0
    
    active_units = get_active_units(unit_dict, active_unit_count)
    setpoints = get_setpoints(active_units, Tlimit_min, Tlimit_max)

    return setpoints
                                             
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
    pass

def query_model(filepath):
    """
    runs queries for multiple possible configurations of the model
    if both possible configurations work it'll choose deadband widening 
    it will also let the user know which queries passed. 
    Testing out behavior of this
    """
    g = rdflib.Graph()
    g.parse(filepath, format = 'ttl')

    queries = {}

    queries['heating_and_cooling_setpoint'] = """
    SELECT DISTINCT *
    WHERE {
        ?zone a s223:DomainSpace ;
            s223:hasProperty ?TZon, ?TsetZonHeat, ?TsetZonCool .

        ?TsetZonCool a app:Heating_Setpoint ;
            ref:hasExternalReference/bacnet:object-name ?TsetZonHeatPoint  .

        ?TsetZonHeat a app:Cooling_Setpoint ;
            ref:hasExternalReference/bacnet:object-name ?TsetZonCoolPoint  .

        ?TZon a app:Zone_Temperature ;
            ref:hasExternalReference/bacnet:object-name  ?TZonPoint  .
        
    }"""

    queries['setpoint_and_mode'] = """
    SELECT DISTINCT *
    WHERE {
        ?zone a s223:DomainSpace ;
            s223:hasProperty ?TZon, ?TsetZon, ?Mode .

        ?TZon a app:Single_Temperature_Setpoint ;
        ref:hasExternalReference/bacnet:object-name ?TsetZonPoint  .

        ?TZon a app:Cooling_Setpoint ;
        ref:hasExternalReference/bacnet:object-name ?TsetZonCoolPoint  .

        ?TsetZon a app:Zone_Temperature ;
        ref:hasExternalReference/bacnet:object-name  ?TZonPoint  .
        
    }"""

    results_dict = {}
    for k, query in queries.items():
        results = g.query(query)
        # only if results have rows add them to the results_dict
        if results:
            results_dict[k] = sparql_to_dict(results)

    return results_dict

def sparql_to_dict(results, key = 'zone'):
    """
    turns results into a dictionary of dictionaries. the key for the containing dictionary can be selected
    turning everything to strings cause it may be easier
    """
    result_dict = {}
    
    for row in results:
        var_names = [var for var in results.vars]
        # Create a dictionary with variable names as keys and corresponding values
        values_dict = {str(var): str(row[var]) for var in var_names[1:]}
        result_dict[str(row[key])] = values_dict

    return result_dict
    