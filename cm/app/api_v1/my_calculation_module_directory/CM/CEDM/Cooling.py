import numpy as np
import shutil
import time, gdal, ogr

import os
import sys
import pickle

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

import CM_intern.CEDM.modules.Subfunctions as SF
import CM_intern.common_modules.array2raster as a2r
import CM_intern.common_modules.cliprasterlayer as  CRL
import CM_intern.CEDM.modules.cyf.SumOfHighRes as SOHR
from CM_intern.common_modules.exportLayerDict import export_layer as expLyr
#import CM_intern.CEDM.modules.cyf.reshape_matrix_py as RSMpy
import CM_intern.CEDM.modules.cyf.reshape_matrix as RSM
import CM_intern.CEDM.modules.DistrCSVDataToMap as DCSV2Map
import  CM_intern.common_modules.readCsvData as RCD

DEBUG = True
DEBUG = False
linux = "linux" in sys.platform
"""
5571
21805
0.5983485579490662
1.0011279582977295
-0.00021568508236669004
0.19121724367141724
0.0
0.4760775864124298
0.0
0.0
0.0

4674
18293
0.4760775864124298
"""

LOWEST_RESOLUTION = 1000 #Meter
# define raster size
#HIGH_TARGET_RESOLUTION = 10 #Meter
FINAL_TARGET_RESOLUTION = 100 #Meter

        
        
#from memory_profiler import profile
#@profile
def _export_layer(SaveLayerDict):
    
    
    print ("Export Layers:")
    st = time.time()
    for k in list(SaveLayerDict.keys()):
        st1 = time.time()
        LL = SaveLayerDict[k]
        print (LL[0])
        if type(LL[3]) is str:
            pass
            print ("already exported")
        else:
            try:
                a2r.array2rasterfileList(LL)
            except Exception as e:
                print (e)
        del SaveLayerDict[k]
        
    print("Process Export Layers took: %4.1f seconds" %(time.time() - st)) 
    
    return(SaveLayerDict)
        


class CALC_cooling_density():

    
    def __init__(self, prj_path
                     , path_in_raw
                     , preproccessed_input_path
                     , results):    
        
        
        
        self.raw_input_data_path = "%s/%s/" % (prj_path, path_in_raw)
        self.results_data_path = "%s/%s/Processed Data/" % (prj_path, results)
        
        self.preproccessed_input_path = "%s/%s/" % (prj_path, preproccessed_input_path)

        
        self.GFA_area = "%s/RESULTS_GFA_TOT_BUILD.tif" % self.results_data_path
        self.rel_CDD = "%s/HDD_CDD_data_new/CDD_EnergyIntensityIndicator.tif" % self.preproccessed_input_path 
        self.NUTSID_map = "%s/NUTS3_id_number.tif" % self.preproccessed_input_path
        
        
        self.csv_NUTS_data = "%s/NUTS3_data.csv" % self.raw_input_data_path
        
        """
        # Standard Vector layer (Nuts 3 shape file)
        self.strd_vector_path_NUTS = self.raw_input_data_path + "/vector_input_data/" + "NUTS3.shp"
        # Standard raster Layer
        self.strd_raster_path_full = self.raw_input_data_path + os.sep + "Population.tif"
        """
        assert os.path.exists(self.GFA_area)
        assert os.path.exists(self.rel_CDD)
        assert os.path.exists(self.NUTSID_map)
        assert os.path.exists(self.csv_NUTS_data)

        
        self.datatype_int = 'int32'
        self.datatype = 'f4'
        self.noDataValue = 0
        
        


        (NUTS_DATA, EXPORT_COLUMNS
            , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_NUTS_data)
        
        A = np.zeros(NUTS_DATA['ENERGY_COOL_per_m2'].shape[0], dtype="f4")
        A[0:] = NUTS_DATA['ENERGY_COOL_per_m2']
        
        ARR_NUTS_ID_NUMBER, geotransform_obj = SF.rrl(self.NUTSID_map, data_type=self.datatype_int)
        
        
        
        ENERGY_COOL_per_m2 = A[ARR_NUTS_ID_NUMBER]   * 0.5 / 1000.0
        
        rel_CDD, geotransform_obj = SF.rrl(self.rel_CDD, data_type=self.datatype)
         
        ENERGY_COOL_per_m2 *= np.minimum(3, rel_CDD)
        
        gfa_tot, geotransform_obj = SF.rrl(self.GFA_area, data_type=self.datatype)
        
        ENERGY_COOL = gfa_tot * ENERGY_COOL_per_m2
        
        SaveLayerDict = {}
        SaveLayerDict["cool"] =   [("%s/%s.tif" %(self.results_data_path, "RESULTS_ENERGY_COOLING_TOT"))
                                                  , geotransform_obj
                                                  , self.datatype
                                                  , ENERGY_COOL, self.noDataValue]
        
        
        
        SaveLayerDict = expLyr(SaveLayerDict)
        print("DONE COOLING")
            
            
        
    
        
   
    
def main(main_path 
        , path_in_raw
        , preproccessed_input_path, results_path):
    
    
    CD = CALC_cooling_density(main_path, path_in_raw
                      , preproccessed_input_path, results_path)
    
   
    
        
     
if __name__ == "__main__":
    
    
    print(sys.version_info)
    
    pr_path = "C:/Hotmaps_DATA/heat_density_map_test"
    pr_path = "Z:/workspace/project/Hotmaps_DATA/heat_density_map/"
    if not os.path.exists(pr_path):
        pr_path = "../../../../../../Hotmaps_DATA/heat_density_map/"
        
    print(os.path.abspath(pr_path))
    print("Path exists: {}".format(os.path.exists(pr_path)))
    assert os.path.exists(pr_path)
    
    
    CD = CALC_cooling_density(main_path, path_in_raw
                      , preproccessed_input_path, results_path)
    
