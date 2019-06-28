import numpy as np

def func_CORINE_LANDCOVER_TRANSFORM_MATRIX():
    # Weigthing maxtric for heat demand based on Corine Land Cover information
    CORINE_LANDCOVER_TRANSFORM_MATRIX = np.zeros(500,dtype="f4") + 0.015
    CORINE_LANDCOVER_TRANSFORM_MATRIX[1] = 1 # Continuous urban fabric
    CORINE_LANDCOVER_TRANSFORM_MATRIX[2] = 0.9 # Discontinuous urban fabric
    
    CORINE_LANDCOVER_TRANSFORM_MATRIX[3] = 0.7 # Industrial or commercial units
    CORINE_LANDCOVER_TRANSFORM_MATRIX[10] = 0.1 # Green urban areas
    CORINE_LANDCOVER_TRANSFORM_MATRIX[11] = 0.1 # Sport and leisure facilities
    CORINE_LANDCOVER_TRANSFORM_MATRIX[18] = 0.5 # Pastures
    CORINE_LANDCOVER_TRANSFORM_MATRIX[20] = 0.5 # Complex cultivation pattern
    CORINE_LANDCOVER_TRANSFORM_MATRIX[21] = 0.5 # Land principally occupied by agriculture
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[4] = 0.1 # Road and rail networks and associated land
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[6] = 0.1 # Airports
    
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[:] = 1
    
    #CORINE_LANDCOVER_TRANSFORM_MATRIX = np.arange(500,dtype="f4") 
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[0] += 0.015
    return CORINE_LANDCOVER_TRANSFORM_MATRIX


def func_CORINE_LANDCOVER_POPULATIONweight():
    """ Weighting factor for Population based Approach (versus OSM approach)
        if 1, then equal weight, if 0.5, then weight of 25% only
    """
    POPULATION_WEIGHT = np.zeros(500,dtype="f4") + 0.5
    POPULATION_WEIGHT[1] = 1 # Continuous urban fabric
    POPULATION_WEIGHT[2] = 1 # Discontinuous urban fabric
    
    POPULATION_WEIGHT[3] = 0.4 # Industrial or commercial units
    POPULATION_WEIGHT[10] = 0.3 # Green urban areas
    POPULATION_WEIGHT[11] = 0.3 # Sport and leisure facilities
    POPULATION_WEIGHT[18] = 0.3 # Pastures
    POPULATION_WEIGHT[20] = 0.8 # Complex cultivation pattern
    POPULATION_WEIGHT[21] = 0.3 # Land principally occupied by agriculture
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[4] = 0.1 # Road and rail networks and associated land
    #CORINE_LANDCOVER_TRANSFORM_MATRIX[6] = 0.1 # Airports

    return POPULATION_WEIGHT
    
    
