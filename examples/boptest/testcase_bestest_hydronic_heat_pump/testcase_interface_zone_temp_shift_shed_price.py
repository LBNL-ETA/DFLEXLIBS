import sys
sys.path.append("..")
from BOPTest_interface_zone_temp_shift_shed_price import (
    BOPTestControls,
    BOPTestControlFunctions,
    BOPTestInterface
)

from utility_functions.get_hvac_signals import (
    get_hydronic_hp_hvac_signals
)

from utility_functions.iterate_lists import (
    iterate_lists_zone_temp_shift_shed_price
)


from utility_functions.get_occ_min import (
    get_occ_min
)


from utility_functions.get_price_threshold import (
    get_price_threshold
)

class TestCaseInterface(BOPTestInterface):
    
    # At the moment I am importing get_hvac_signals, however, the function could just be written here directly
    def get_hvac_signals(self, *args):
        return get_hydronic_hp_hvac_signals(*args)
    
    def iterate_lists(self, *args):
        return iterate_lists_zone_temp_shift_shed_price(*args)
    
    def get_occ_min(self, *args):
        return get_occ_min(*args)
    
    def get_price_threshold(self, *args):
        return get_price_threshold(*args)
    
def create_application(config_path) -> BOPTestInterface: 
    '''takes a config file and returns an instantiated TestCaseInterface
    
    Parameters
    ----------
        config_path : str
            the path to a configuration file for instantiating a bestest hydronic heat pump shift and shed application 
    Returns
    -------
        application : BestetsAirInterface
            returns an instantiated bestest hydronic heat pump interface with shifting and shedding controls
'''
    functions = BOPTestControlFunctions()
    controls = BOPTestControls(functions)
    application  = TestCaseInterface(controls, config_path)
    
    return application

