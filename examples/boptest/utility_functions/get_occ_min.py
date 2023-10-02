def get_occ_min(occupancy_schedule):
    import numpy as np

    occ = occupancy_schedule.copy()
    
    if all(x == occ[0] for x in occ):
        # Reset minimal occupancy in case of all values of the list are equal (for example, over the weekend)
        occMinThreshold = 0
    else: 
        occMinThreshold = np.min(occ)
    return occMinThreshold
