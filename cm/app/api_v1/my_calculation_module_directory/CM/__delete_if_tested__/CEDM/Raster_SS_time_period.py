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

#import CM_intern.CEDM.modules.cyf.reshape_matrix_py as RSMpy
import CM_intern.CEDM.modules.cyf.reshape_matrix as RSM

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
        


class ConstrShares():

    
    def __init__(self, prj_path
                     , path_in_raw
                     , preproccessed_input_path):    
        
        
        
        self.raw_input_data_path = "%s/%s/" % (prj_path, path_in_raw)
        
        self.preproccessed_input_path = "%s/%s/" % (prj_path, preproccessed_input_path)
         
        self.SoilSeal_input_data_path = "%s/SS_history/gdalwarp_EUROPE/" % self.raw_input_data_path  

        self.outputdir_path = "%s/SoilSeal_ConstrPeriods/" % self.preproccessed_input_path 
        self.CPbasedEnergyIntensity_fn_path = "%s/CPbased_EnergyIntensity.tif" % self.outputdir_path 
        
        
        self.SoilSeal_output_data_path = "%s/" % self.outputdir_path
        
        self.SoilSealingFile = "%s/SS2012.tif" % self.raw_input_data_path
        
        self.BUILD_UP_SoilSealingFIle = "%s/_____ESM100m_final.tif" % self.raw_input_data_path
        
        if os.path.exists(self.outputdir_path) == False:
            os.makedirs(self.outputdir_path) 
        
       
        # Standard Vector layer (Nuts 3 shape file)
        self.strd_vector_path_NUTS = self.raw_input_data_path + "/vector_input_data/" + "NUTS3.shp"
        # Standard raster Layer
        self.strd_raster_path_full = self.raw_input_data_path + os.sep + "Population.tif"

        

        
        self.datatype_int = 'int32'
        self.datatype = 'f4'
        self.noDataValue = 0
        
        
    
        
    #@profile
    def CreateNewSoilSeal_TIME_layer(self ):
        
        
        

        key_field = "NUTS_ID"
        
        self.REFERENCE_RASTER_LAYER_COORD = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(self.strd_raster_path_full
                    , self.strd_vector_path_NUTS, []
                    , Vctr_key_field=key_field)
        (self.REFERENCE_geotransform_obj, self.REFERENCE_RasterSize, self.REFERENCE_RESOLUTION, self.REFERENCE_extent), uncut = self.REFERENCE_RASTER_LAYER_COORD
        SaveLayerDict = {}
        SaveLayerDict["Reference"] =   ["%s/REFERENCE.tiff" % self.outputdir_path, self.REFERENCE_geotransform_obj
                                                      , self.datatype_int
                                                      , np.ones((self.REFERENCE_RasterSize), dtype=self.datatype_int) , self.noDataValue]
        SaveLayerDict = _export_layer(SaveLayerDict)
        """
        arr_pop_cut, geotransform_obj = CRL.clip_raster_layer(self.strd_raster_path_full
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   
        """
        SaveLayerDict = {}
        

            
        st_n = time.time()
        for period in [1975, 1990, 2000, 2014]:                 #
                
            fn = "%s/GHS_BUILT_LDS%s_3035.tif" %(self.SoilSeal_input_data_path, str(period))
            fn_new_res = "%s/GHS_BUILT_LDS%s_3035_new.tif" % (self.SoilSeal_output_data_path, str(period))
            
            print("  : Image %s -> %s" %(period, fn))
            SS_period_240, geotransform_obj = SF.rrl(fn, data_type=self.datatype)
            st0 =time.time()
            RESOLUTION = (FINAL_TARGET_RESOLUTION / geotransform_obj[1]
                          , FINAL_TARGET_RESOLUTION / -geotransform_obj[5])
            print(np.sum(SS_period_240) / 10 ** 6)
            RESULTS_MATRIX = RSM.reshapeM(SS_period_240, RESOLUTION
                                          , adopt_values = 0)
            #RESULTS_MATRIX = RSMpy.reshapeM(POPnew_240, RESOLUTION)
            print("Reshape Image took:  %4.1f sec" % (time.time() - st0))
            print(np.sum(RESULTS_MATRIX) / 10 ** 6)
            print(np.max(RESULTS_MATRIX))
            print(np.min(RESULTS_MATRIX))
            print(np.sum(RESULTS_MATRIX >1000))
            geotransform_obj_newRes = (geotransform_obj[0], FINAL_TARGET_RESOLUTION,0,
                                       geotransform_obj[3], 0, - FINAL_TARGET_RESOLUTION)
            
            """
            
            
            SaveLayerDict["popnewres"] =   [fn_new_res, geotransform_obj_newRes
                                                      , self.datatype
                                                      , RESULTS_MATRIX , self.noDataValue]
            #SaveLayerDict = _export_layer(SaveLayerDict)
            
            """
            print(" clip_raster_layer array")
            (RESULTS_MATRIX_clipped, geotransform_obj_clipped) = CRL.clip_raster_layer([RESULTS_MATRIX, geotransform_obj_newRes] 
                                                        , self.REFERENCE_geotransform_obj
                                                        , self.REFERENCE_RasterSize
                                                        , return_offset_list = False
                                                        , final_res=1000)  
            
            (data_SS_CLC_500_m) = SOHR.CalcLowResSum(RESULTS_MATRIX_clipped, 5)
            geotransform_obj_clipped_500 = (geotransform_obj_clipped[0], geotransform_obj_clipped[1]*5, 0
                                            , geotransform_obj_clipped[3], 0, geotransform_obj_clipped[5]*5)
            (data_SS_CLC_1_km) = SOHR.CalcLowResSum(data_SS_CLC_500_m, 2)
            geotransform_obj_clipped_1km = (geotransform_obj_clipped[0], geotransform_obj_clipped[1]*10, 0
                                            , geotransform_obj_clipped[3], 0, geotransform_obj_clipped[5]*10)
            SaveLayerDict["SoilSealnewres_100"] =   ["%s_100.tif" % fn_new_res[:-4], geotransform_obj_clipped
                                                      , self.datatype
                                                      , RESULTS_MATRIX_clipped , self.noDataValue]
            SaveLayerDict["SoilSealnewres_500"] =   ["%s_500.tif" % fn_new_res[:-4], geotransform_obj_clipped_500
                                                      , self.datatype
                                                      , data_SS_CLC_500_m , self.noDataValue]
            SaveLayerDict["SoilSealnewres_1km"] =   ["%s_1km.tif" % fn_new_res[:-4], geotransform_obj_clipped_1km
                                                      , self.datatype
                                                      , data_SS_CLC_1_km , self.noDataValue]
            SaveLayerDict = _export_layer(SaveLayerDict)
            print("Done")
        
        print("Process took:  %4.1f sec" % (time.time() - st_n))
    
        print("DONE!")
    
    
        #for period in [1975, 1990, 2000, 2014]:                 #
    def calc_shares_construction_period(self):       
        
        
        
        
        key_field = "NUTS_ID"
        RESOLUTION = "100"
        
        self.REFERENCE_RASTER_LAYER_COORD, uncut = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(self.strd_raster_path_full
                    , self.strd_vector_path_NUTS, []
                    , Vctr_key_field=key_field)
        (self.REFERENCE_geotransform_obj, self.REFERENCE_RasterSize, self.REFERENCE_RESOLUTION, self.REFERENCE_extent) = self.REFERENCE_RASTER_LAYER_COORD
        
        
        
        SoilSeal2012, geotransform_obj = CRL.clip_raster_layer(self.SoilSealingFile
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize) 
        SoilSealBuildUp, geotransform_obj = CRL.clip_raster_layer(self.BUILD_UP_SoilSealingFIle
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   
        
        
        fn_14 = "%s/GHS_BUILT_LDS2014_3035_new_%s.tif" %(self.SoilSeal_output_data_path, RESOLUTION)
        fn_share_14 = "%s/GHS_BUILT_2014_%s_share.tif" % (self.SoilSeal_output_data_path, RESOLUTION)  
            
        SoilSeal_14, geotransform_obj = SF.rrl(fn_14, data_type=self.datatype)
        
        SoilSeal2012[SoilSeal2012 > 100] =0
        Estimated_share_build_SoilSeal =  np.minimum(1, SoilSealBuildUp / (0.0001 + 0.5 * (SoilSeal_14 + SoilSeal2012 /100.0)))
        del SoilSealBuildUp, SoilSeal2012
        SaveLayerDict = {}
        
        
        fn_75 = "%s/GHS_BUILT_LDS1975_3035_new_%s.tif" %(self.SoilSeal_output_data_path, RESOLUTION)
        fn_share_75 = "%s/GHS_BUILT_1975_%s_share.tif" % (self.SoilSeal_output_data_path, RESOLUTION)
        
        fn_90 = "%s/GHS_BUILT_LDS1990_3035_new_%s.tif" %(self.SoilSeal_output_data_path, RESOLUTION)
        fn_share_90 = "%s/GHS_BUILT_1990_%s_share.tif" % (self.SoilSeal_output_data_path, RESOLUTION)
            
        fn_00 = "%s/GHS_BUILT_LDS2000_3035_new_%s.tif" %(self.SoilSeal_output_data_path, RESOLUTION)
        fn_share_00 = "%s/GHS_BUILT_2000_%s_share.tif" % (self.SoilSeal_output_data_path, RESOLUTION)
        
            
        print("Load Images")
        SoilSeal_75, geotransform_obj = SF.rrl(fn_75, data_type=self.datatype)
        SoilSeal_90, geotransform_obj = SF.rrl(fn_90, data_type=self.datatype)
        SoilSeal_00, geotransform_obj = SF.rrl(fn_00, data_type=self.datatype)
        
        
        print ("Loaded")
        SoilSeal_7590 = np.maximum(SoilSeal_90 * 0.0075, SoilSeal_90 - SoilSeal_75 * (1 - 0.001) ** 15)
        SoilSeal_9000 = np.maximum(SoilSeal_00 * 0.0075, SoilSeal_00 - SoilSeal_7590 - SoilSeal_75 * (1 - 0.001) ** 25)
        SoilSeal_0014 = np.maximum(SoilSeal_14 * 0.0075, SoilSeal_14 - SoilSeal_9000 - SoilSeal_7590 * (1 - 0.001) ** 25 - SoilSeal_75 * (1 - 0.001) ** 40)                   
        
        SaveLayerDict["SoilSeal7590"] =   ["%s_CP7590.tif" % fn_share_90[:-9], geotransform_obj
                                                      , self.datatype
                                                      , SoilSeal_7590 , self.noDataValue]
        SaveLayerDict["SoilSeal9000"] =   ["%s_CP9000.tif" % fn_share_00[:-9], geotransform_obj
                                                  , self.datatype
                                                  , SoilSeal_9000 , self.noDataValue]
        SaveLayerDict["SoilSeal0014"] =   ["%s_CP0014.tif" % fn_share_14[:-9], geotransform_obj
                                                  , self.datatype
                                                  , SoilSeal_0014 , self.noDataValue]
        SaveLayerDict = _export_layer(SaveLayerDict)
        
        # Estimated Soil Sealing in 2014 per construction period    
        SS_be75 = SoilSeal_75 * (1 - 0.001) ** 40 * (1 + Estimated_share_build_SoilSeal) / 2
        
        SaveLayerDict["Estimated_share_no_build_SoilSeal"] =   ["%s/Estimated_share_build_SoilSeal.tif" % self.SoilSeal_output_data_path, geotransform_obj
                                          , self.datatype
                                          , Estimated_share_build_SoilSeal , self.noDataValue]
        
        SaveLayerDict = _export_layer(SaveLayerDict)
        del Estimated_share_build_SoilSeal   
        SS_7590 = SoilSeal_7590 * (1 - 0.001) ** 25
        SS_9000 = SoilSeal_9000
        SS_0014 = SoilSeal_0014         
        
        TotalSum_Soil_Seal = np.maximum(0.000001, SS_be75 + SS_7590 + SS_9000 + SS_0014)
        
        SS_be75 /= TotalSum_Soil_Seal
        SS_7590 /= TotalSum_Soil_Seal
        SS_9000 /= TotalSum_Soil_Seal
        SS_0014 /= TotalSum_Soil_Seal
        del TotalSum_Soil_Seal
        SaveLayerDict["SoilSealbe7590"] =   [fn_share_75, geotransform_obj
                                                      , self.datatype
                                                      , SS_be75 , self.noDataValue]       
        SaveLayerDict["SoilSeal7590"] =   [fn_share_90, geotransform_obj
                                                      , self.datatype
                                                      , SS_7590 , self.noDataValue]
        SaveLayerDict["SoilSeal9000"] =   [fn_share_00, geotransform_obj
                                                  , self.datatype
                                                  , SS_9000 , self.noDataValue]
        SaveLayerDict["SoilSeal0014"] =   [fn_share_14, geotransform_obj
                                                  , self.datatype
                                                  , SS_0014 , self.noDataValue]
        


        CP_based_WeightedEnergyIndicator = (SS_9000 * 1 
                                            + SS_0014 * 0.8 
                                            + SS_7590 * 1.25
                                            + SS_be75 * 1.25)
        
        SaveLayerDict["CPbased_EnergyIntensity"] =   [self.CPbasedEnergyIntensity_fn_path, geotransform_obj
                                                  , self.datatype
                                                  , CP_based_WeightedEnergyIndicator , self.noDataValue]
        
        SaveLayerDict = _export_layer(SaveLayerDict)
        print("DONE!")

    
def main(main_path 
        , path_in_raw
        , preproccessed_input_path):
    
    
    CD = ConstrShares(main_path, path_in_raw
                      , preproccessed_input_path)
    
    CD.CreateNewSoilSeal_TIME_layer()

    CD.calc_shares_construction_period()
    
        
     
if __name__ == "__main__":
    
    
    print(sys.version_info)
    
    pr_path = "C:/Hotmaps_DATA/heat_density_map_test"
    pr_path = "Z:/workspace/project/Hotmaps_DATA/heat_density_map/"
    if not os.path.exists(pr_path):
        pr_path = "../../../../../../Hotmaps_DATA/heat_density_map/"
        
    print(os.path.abspath(pr_path))
    print("Path exists: {}".format(os.path.exists(pr_path)))
    assert os.path.exists(pr_path)
    CD = ConstrShares(pr_path)
    
    CD.CreateNewSoilSeal_TIME_layer()

    CD.calc_shares_construction_period()
    

