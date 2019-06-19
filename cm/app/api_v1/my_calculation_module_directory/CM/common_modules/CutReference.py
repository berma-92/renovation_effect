import numpy as np
import shutil
import time, gdal, ogr

import os
import sys




path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

#import  CM_intern.CEDM.modules.Subfunctions as SF

#import  modules.changeRastExt as cre   # import RastExtMod
#import  CM_intern.CEDM.modules.higherRes as hr        # import HighRes
#import  CEDM.modules.query as qu
#import  CEDM.modules.rasterize as ra
#import  CM_intern.common_modules.readCsvData as RCD

#import common_modules.array2raster as a2r
#import CM_intern.CEDM.modules.cyf.SumOfHighRes_64 as SOHR
#import CM_intern.CEDM.modules.cyf.create_density_map_64 as CDM
#import CEDM.modules.cyf.create_density_map_py as CDMpy
#import CEDM.modules.cyf.SumOfHighRes_py as SOHRpy
import CM_intern.common_modules.cliprasterlayer as CRL

from CM_intern.common_modules.exportLayerDict import export_layer as expLyr
#from CM_intern.CEDM.modules.createIndexRasterMap import createIndexMap 

#import CEDM.modules.DistrCSVDataToMap as DCSV2Map


import pickle

COMPRESSION_LEVEL_FINAL_RESULTS = 9

DEBUG = True
#DEBUG = False
PRINT_TEST_RESULTS = False
EXPORT_AT_THE_END = False # IF TRUE, THAN RESULTS ARE PRINTED FASTER; yet more RAM required

linux = "linux" in sys.platform


import  CM_intern.CEDM.modules.CorineLCTransformVector as CLCTV
# Weigthing maxtric for heat demand based on Corine Land Cover information
CORINE_LANDCOVER_TRANSFORM_MATRIX = CLCTV.func_CORINE_LANDCOVER_TRANSFORM_MATRIX()
CORINE_LANDCOVER_POPWeight = CLCTV.func_CORINE_LANDCOVER_POPULATIONweight()

LOWEST_RESOLUTION = 1000 #Meter
# define raster size
TARGET_RESOLUTION = 100 #Meter





class ClassCalcDensity():
    
    def __init__(self, prj_path, prj_path_input, prj_path_output ):
        
        #Raise error if Data path doesn't exist
        print("Project Path: %s" % os.path.abspath(prj_path))
        if not os.path.exists(prj_path):
            print("Project Path doesn't exist")
        
        assert(os.path.exists(prj_path))
        self.prj_path = prj_path
        
        # Input data path 
        org_data_path = prj_path  + os.sep + prj_path_input 
        if not os.path.exists(org_data_path):
            print("Input data path doesn't exist : %s" % org_data_path)
        
        self.org_data_path = org_data_path
        
        # final output path      
        self.prj_path_output    = "%s/%s" %(prj_path, prj_path_output)  
        
        
        # input data files
        # Standard Vector layer (Nuts 3 and LAU shape file)
        self.NUTS3_vector_path = self.org_data_path + "/vector_input_data/NUTS3.shp"


        # Standard raster Layer
        self.strd_raster_path_full = "%s/%s" %(self.org_data_path, "Population.tif")
        
        
        
        #outputs
        self.MOST_RECENT_CUT = "%s/MOST_RECENT_CUT.pk" %self.prj_path_output 

        
        
        
      
        # array2raster output datatype
        self.datatype_int = 'uint32'
        
        # common parameters
        self.noDataValue = 0
        
        
        (REFERENCE_RasterResolution, HighRes_gt_obj, self.LOAD_DATA_PREVIOUS) = \
                self.load_reference_raster_lyr(self.NUTS3_vector_path,
                                               self.strd_raster_path_full, 
                                               self.prj_path_output, NUTS3_feat_id_LIST)
                
        return
          
    def load_reference_raster_lyr(self, NUTS3_vector_path, strd_raster_path_full, outputpath, NUTS3_feat_id_LIST, deletedata=True):
        
        #SaveLayerDict = {}
        # Get current extent -> Use the Population 1x1km raster as reference Layer
        key_field = "NUTS_ID" 
        REFERENCE_RASTER_LAYER_COORD = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(strd_raster_path_full
                    , NUTS3_vector_path, NUTS3_feat_id_LIST
                    , Vctr_key_field=key_field)
        (self.REFERENCE_geotransform_obj, self.REFERENCE_RasterSize
         , self.REFERENCE_RESOLUTION, self.REFERENCE_extent), _ = REFERENCE_RASTER_LAYER_COORD
        
        REFERENCE_RasterResolution = self.REFERENCE_geotransform_obj[1]
        
        gto_hr = list(self.REFERENCE_geotransform_obj)
        gto_hr[1] = TARGET_RESOLUTION
        gto_hr[5] = -TARGET_RESOLUTION
        HighRes_gt_obj = tuple(gto_hr)
        
        SaveLayerDict = {}
        SaveLayerDict["Reference"] =   ["%s/REFERENCE.tif" % outputpath, self.REFERENCE_geotransform_obj
                                                      , self.datatype_int
                                                      , np.ones((self.REFERENCE_RasterSize), dtype=self.datatype_int) , self.noDataValue]
        
        
        # If data are the same as previous cut, then loading data can be done
        LOAD_DATA_PREVIOUS = False
        filename = self.MOST_RECENT_CUT
        if os.path.exists(self.MOST_RECENT_CUT):
            try:
                with open(self.MOST_RECENT_CUT, 'rb') as fobject:
                    PREV_CUT = pickle.load(fobject)
                    fobject.close()
                if PREV_CUT == REFERENCE_RASTER_LAYER_COORD:
                    LOAD_DATA_PREVIOUS = True
            except Exception as e:
                print("Cannot import %s"%self.MOST_RECENT_CUT)
                print(e)
        
        
            
        if not os.path.exists(outputpath):
            os.makedirs(outputpath) 
        
            
        with open(filename, 'wb') as fobject:
            pickle.dump(REFERENCE_RASTER_LAYER_COORD, fobject, protocol=2)
            fobject.close()
        SaveLayerDict = expLyr(SaveLayerDict)
        
        return (REFERENCE_RasterResolution, HighRes_gt_obj, LOAD_DATA_PREVIOUS)
    
        
def main(pr_path, prj_path_input, prj_path_output
         , NUTS3_feat_id_LIST, preproccessed_input_path):
    
    
    
    CD = ClassCalcDensity(pr_path, prj_path_input, prj_path_output)


    
    
    return       
        
        
if __name__ == "__main__":
    
    print(sys.version_info)
    print(os.getcwd())
    pr_path = "C:/Hotmaps_DATA/heat_density_map_test"
    if not os.path.exists(pr_path):
        pr_path = "../../../../../../Hotmaps_DATA/heat_density_map2"
    
    #Nuts3 Regions
    NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
    
    #NUTS3_feat_id_LIST = range(14)
    #NUTS3_feat_id_LIST = range(603,615)
    #NUTS3_feat_id_LIST = range(1300,15000)
    NUTS3_feat_id_LIST = ["AT"]
    NUTS3_feat_id_LIST = range(10,15)
    #main(pr_path, prj_path_output, NUTS3_feat_id_LIST)
    #NUTS3_feat_id_LIST = range(500)
    #NUTS3_feat_id_LIST = range(30)
    #NUTS3_feat_id_LIST = range(10)
    #NUTS3_feat_id_LIST = [14]  
    #NUTS3_feat_id_LIST = range(100)
    #NUTS3_feat_id_LIST = range(10,15)
    prj_path_output = "output_findme"
    
    
    prj_path_input = "0_inputdata_raw"
    preproccessed_input_path = "1_inputdata_preproccessed"
    #prj_path_input =  "Input Data_cut"
    #prj_path_output = "output_test_ch"
    #NUTS3_feat_id_LIST = ["CH"]
    
        
    main(pr_path, prj_path_input, prj_path_output
         , NUTS3_feat_id_LIST, preproccessed_input_path)
    
    #start()
    print("Done!")