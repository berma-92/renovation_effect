'''
Created on Feb 3, 2018

@author: simulant
'''
import time
import numpy as np
import sys
import os

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
    
import common_modules.readCsvData as RCD
import CEDM.modules.cyf.create_density_map as CDM
from common_modules.exportLayerDict import export_layer as expLyr


def dist_csv_data2map(final_maps_output_path, noDataValue
              , DENSITY_MAP, geotransform_Object
              , NUTS_ID_MAP
              , csv_input_data_file
              , ColumnStartsWith=""
              , PRINT_TEST_RESULTS = False
              , COMPRESSION_LEVEL_FINAL_RESULTS = 9
              , TARGET_RESOLUTION = 100
              , ADD_ID_MAP= {}
              , filename_prefix = ""
              , COLNAME_ID_INDICATOR = "NUTS_CODE"
              , CUT_OFF = False):
    
    SaveLayerDict = {}
    #print("Process 5")
    
    datatype = "float32"
    
    st1 = time.time()
    
    
    (NUTS3_DATA, EXPORT_COLUMNS
        , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(csv_input_data_file)
    num_res = len(EXPORT_COLUMNS)
    for i in range(num_res ):
        COLUMN_NAME = EXPORT_COLUMNS[i]
        
        if not COLUMN_NAME.startswith(ColumnStartsWith):
            continue
        print("Create Data Array Nr. %i: %s" % (i + 1, COLUMN_NAME))
        NUTS_Data  = NUTS3_DATA.view(np.recarray)[COLUMN_NAME]
        if SCALING_FACTOR[i] != 0:
            NUTS_Data *= SCALING_FACTOR[i]
        RESULT_Array = CDM.CreateFinalMap(DENSITY_MAP, NUTS_ID_MAP, NUTS_Data)
             
        if PRINT_TEST_RESULTS == True:
            NUTS_REGIONS = np.unique(NUTS_ID_MAP)
            
            DEBUG_RES = []
            for j in range(len(NUTS_REGIONS)):
                NUTSREG = NUTS_REGIONS[j]
                idxM = NUTS_ID_MAP == NUTSREG
                newRes = np.sum(RESULT_Array[idxM])
                origData = NUTS_Data[NUTSREG]
                DEBUG_RES.append("%i: %s  %5.2f (%s) - %5.2f" 
                      %(NUTSREG
                        , NUTS3_DATA.view(np.recarray)[COLNAME_ID_INDICATOR][NUTSREG]
                        , newRes, "%5.2f"
                        , origData))

        if CUT_OFF == True:
            RESULT_Array[RESULT_Array < CUTOFF_Value[i]] = 0
        
        if PRINT_TEST_RESULTS == True:
            for j in range(len(NUTS_REGIONS)):
                NUTSREG = NUTS_REGIONS[j]
                idxM = NUTS_ID_MAP == NUTSREG
                newRes = np.sum(RESULT_Array[idxM])
                DEBUG_RES[j] = DEBUG_RES[j] % newRes
                print(DEBUG_RES[j] % newRes)
          
        filename = "%sRESULTS_%s" % (filename_prefix, COLUMN_NAME)
        SaveLayerDict[filename] = ("%s/%s.tif" %(final_maps_output_path, filename)
                            , geotransform_Object
                            , datatype
                            , RESULT_Array, noDataValue
                            , COMPRESSION_LEVEL_FINAL_RESULTS)
        
        SaveLayerDict = expLyr(SaveLayerDict)
        
        TABLE_RESULTS = CDM.CreateResultsTableperIndicator(RESULT_Array, NUTS_ID_MAP)   
        np.savetxt("%s/%s.csv" %(final_maps_output_path, filename), np.round(TABLE_RESULTS, 0), delimiter=",")
        st = time.time()
        for IDMAP_key in ADD_ID_MAP.keys():
            
            TABLE_RESULTS = CDM.CreateResultsTableperIndicator(RESULT_Array, ADD_ID_MAP[IDMAP_key])   
            np.savetxt("%s/%s_%s.csv" %(final_maps_output_path, filename, IDMAP_key), np.round(TABLE_RESULTS, 0), delimiter=",")
        print("Time to export Data to csv: %4.1f sec" % (time.time() - st)) 
        
        m2_per_px = TARGET_RESOLUTION ** 2
        RESULT_Array /= m2_per_px
        SaveLayerDict[filename] = ("%s/%s_per_m2_plot_area.tif" %(final_maps_output_path, filename)
                            , geotransform_Object
                            , datatype
                            , RESULT_Array, noDataValue
                            , COMPRESSION_LEVEL_FINAL_RESULTS)
        
        SaveLayerDict = expLyr(SaveLayerDict)
        
        
    print ("Create Results took: %5.1f sec" % (time.time() - st1))

    return SaveLayerDict