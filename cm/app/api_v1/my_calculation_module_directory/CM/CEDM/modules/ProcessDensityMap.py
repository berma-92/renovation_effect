'''
Created on Feb 18, 2018

@author: simulant
'''
import time
import sys
import numpy as np

from common_modules.exportLayerDict import export_layer as expLyr
import CEDM.modules.cyf.create_density_map_64 as CDM


def process_density_map(output_path, noDataValue
              , pop_density_indicator_map, geotransform_Object
              , REGION_ID_MAP
              , OSM_BGF
              , OSM_DataWeight
              , POP_Weight
              , POSTFIX_fn=""
              , DEBUG = True):
    
    SaveLayerDict = {}
    print("Process Density Map")
    
    datatype = "float32"
    
    st1 = time.time()
    DENSITY_MAP_POP = CDM.CreateDensistyMap(pop_density_indicator_map, REGION_ID_MAP)
    
    if type(DENSITY_MAP_POP).__name__ != 'ndarray':
        sys.exit()
    
    if DEBUG:
        filename = "DENSITY_MAP_POP_based_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , DENSITY_MAP_POP, noDataValue)
    
        SaveLayerDict = expLyr(SaveLayerDict)
        TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP_POP, REGION_ID_MAP)   
        np.savetxt("%s/%s.csv" %(output_path, filename), np.round(TABLE_RESULTS, 0), delimiter=",")
        
    print ("CreateDensistyMap POP based took: %5.1f sec" % (time.time() - st1)) 
    
    DENSITY_MAP_OSM = CDM.CreateDensistyMap(OSM_BGF, REGION_ID_MAP)
    
    del OSM_BGF
    if type(DENSITY_MAP_OSM).__name__ != 'ndarray':
        sys.exit()
    
    if DEBUG:
        filename = "DENSITY_MAP_OSM_based_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , DENSITY_MAP_OSM, noDataValue)
        TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP_OSM, REGION_ID_MAP)   
        np.savetxt("%s/%s.csv" %(output_path, filename), np.round(TABLE_RESULTS, 0), delimiter=",")
        
        filename = "DENSITY_MAP_OSM_Weight_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , OSM_DataWeight, noDataValue)
        filename = "DENSITY_MAP_POP_Weight_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , POP_Weight, noDataValue)
        
        SaveLayerDict = expLyr(SaveLayerDict)
    print ("CreateDensistyMap OSM based took: %5.1f sec" % (time.time() - st1))     
    
    combined_density_indicator_map = (DENSITY_MAP_OSM * (OSM_DataWeight + (1 - POP_Weight))
                              + DENSITY_MAP_POP * (1 + POP_Weight - OSM_DataWeight)) * 0.5
    
    del DENSITY_MAP_OSM, DENSITY_MAP_POP, OSM_DataWeight, POP_Weight
    
    DENSITY_MAP = CDM.CreateDensistyMap(combined_density_indicator_map, REGION_ID_MAP)
    TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP, REGION_ID_MAP)   
    np.savetxt("%s/%s.csv" %(output_path, "DENSITY_MAP_combined_%s" % POSTFIX_fn), np.round(TABLE_RESULTS, 0), delimiter=",")
    
    
    print ("CreateDensistyMap took: %5.1f sec" % (time.time() - st1))
    return DENSITY_MAP