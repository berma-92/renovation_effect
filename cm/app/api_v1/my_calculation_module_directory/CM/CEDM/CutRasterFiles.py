import numpy as np
import shutil
import time, gdal, ogr

import os
import sys

from memory_profiler import profile


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



COMPRESSION_LEVEL_FINAL_RESULTS = 9

DEBUG = True
#DEBUG = False
PRINT_TEST_RESULTS = False
EXPORT_AT_THE_END = False # IF TRUE, THAN RESULTS ARE PRINTED FASTER; yet more RAM required

linux = "linux" in sys.platform



LOWEST_RESOLUTION = 1000 #Meter
# define raster size
TARGET_RESOLUTION = 100 #Meter





class CutRasterFiles():
    
    def __init__(self, standardraster_path, prj_path_input ):
        
        #Raise error if Data path doesn't exist
        print("Standard Raster Path: %s" % os.path.abspath(standardraster_path))
        if not os.path.exists(standardraster_path):
            print("Standard Raster  Path doesn't exist")
            
        print("Project Path: %s" % os.path.abspath(prj_path_input))
        if not os.path.exists(prj_path_input):
            print("Project Path doesn't exist")
        
        assert(os.path.exists(standardraster_path) and os.path.exists(prj_path_input))

        # Input data path         
        self.input_path = prj_path_input
        
        self.output_path = "%s/output" % self.input_path
        #create if doesn't exist
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # input data files
        # Standard Vector layer (Nuts 3 and LAU shape file)
        self.NUTS3_vector_path = standardraster_path + "/vector_input_data/NUTS3.shp"
        
        # Standard raster Layer
        self.strd_raster_path_full = "%s/%s" %(standardraster_path, "Population.tif")
        
      
        # array2raster output datatype
        self.datatype_int = 'uint32'
        #self.datatype_int16 = 'uint16'
        datatype = "float32"
        # common parameters
        self.noDataValue = 0
        
        self.files2cut = {} 
        self.files2cut["CP_share_1975"] = ("GHS_BUILT_1975_100_share.tif"
                                           , "GHS_BUILT_1975_100_share.tif"
                                           , datatype)
        self.files2cut["CP_share_1990"] = ("GHS_BUILT_1990_100_share.tif"
                                           , "GHS_BUILT_1990_100_share.tif"
                                           , datatype)
        self.files2cut["CP_share_2000"] = ("GHS_BUILT_2000_100_share.tif"
                                           , "GHS_BUILT_2000_100_share.tif"
                                           , datatype)
        self.files2cut["CP_share_2014"] = ("GHS_BUILT_2014_100_share.tif"
                                           , "GHS_BUILT_2014_100_share.tif"
                                           , datatype)
        self.files2cut["NUTS3_id"] = ("NUTS3_cut_id_number.tif"
                                           , "NUTS3_cut_id_number.tif"
                                           , datatype)
                          
    def load_reference_raster_lyr(self, NUTS3_vector_path
                                  , strd_raster_path_full
                                  , outputpath, NUTS3_feat_id_LIST):
        
        #SaveLayerDict = {}
        # Get current extent -> Use the Population 1x1km raster as reference Layer
        key_field = "NUTS_ID" 
        REFERENCE_RASTER_LAYER_COORD = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(strd_raster_path_full
                    , NUTS3_vector_path, NUTS3_feat_id_LIST
                    , Vctr_key_field=key_field)
        (self.REFERENCE_geotransform_obj, self.REFERENCE_RasterSize
         , self.REFERENCE_RESOLUTION, self.REFERENCE_extent) = REFERENCE_RASTER_LAYER_COORD
        
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
        SaveLayerDict = expLyr(SaveLayerDict)
        
        return (REFERENCE_RasterResolution, HighRes_gt_obj, self.REFERENCE_geotransform_obj)
    
    def main_process(self, NUTS3_feat_id_LIST):
        
        
        
        
        start_time = time.time()
        
        SaveLayerDict = {}
        # Load Raster Reference Layer
        (REFERENCE_RasterResolution, HighRes_gt_obj
         , REFERENCE_geotransform_obj) = \
                self.load_reference_raster_lyr(self.NUTS3_vector_path,
                                               self.strd_raster_path_full, 
                                               self.output_path, NUTS3_feat_id_LIST)
        
        for key_ in self.files2cut.keys():
            print(key_)
            (fn_in, fn_out, datatype)  = self.files2cut[key_]
            fn_in_fp = "%s/%s"%(self.input_path, fn_in)
            
            fn_out_fp = "%s/%s"%(self.output_path, fn_out)
            
            assert(os.path.exists(fn_in_fp))
            RASTER, geotransform_obj = CRL.clip_raster_layer(fn_in_fp
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize) 
            print("  Data read")
            SaveLayerDict["key_"] =   (fn_out_fp, geotransform_obj
                                        , datatype, RASTER , self.noDataValue)
            SaveLayerDict = expLyr(SaveLayerDict)
            
            print("Done %5.2f"%(time.time() - start_time))    
        
        print("Done")
        return                                 
                                                 
if __name__ == "__main__":
    
    print(sys.version_info)
    print(os.getcwd())
    pr_path = "C:/Hotmaps_DATA/heat_density_map_test"
    if not os.path.exists(pr_path):
        pr_path = "../../../../../../Hotmaps_DATA/heat_density_map"
    
    
    #Nuts3 Regions
    #NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    #NUTS3_feat_id_LIST = range(0,20000)  
    
    NUTS3_feat_id_LIST = range(700)
    #NUTS3_feat_id_LIST = range(603,615)
    #NUTS3_feat_id_LIST = range(1300,15000)
    #NUTS3_feat_id_LIST = ["DK"]
    #main(pr_path, prj_path_output, NUTS3_feat_id_LIST)
    #NUTS3_feat_id_LIST = range(500)
    #NUTS3_feat_id_LIST = range(30)
    #NUTS3_feat_id_LIST = range(10)
    prj_path_output = "output"
    
    prj_path_input = "Input Data"
    
    #prj_path_input =  "Input Data_cut"
    #prj_path_output = "output_test_ch"
    #NUTS3_feat_id_LIST = ["CH"]
    
    standardraster_path= "%s/%s" % (pr_path, "Input Data" )
    prj_path_input= "%s/%s" % (pr_path, "CUT_RASTER_FILES" )

    
    CD = CutRasterFiles(standardraster_path, prj_path_input)
    CD.main_process(NUTS3_feat_id_LIST)
    
    
    #start()
    print("Done!")                                            
