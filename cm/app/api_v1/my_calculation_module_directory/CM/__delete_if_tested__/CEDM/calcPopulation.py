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

import  CM_intern.CEDM.modules.Subfunctions as SF

#import  modules.changeRastExt as cre   # import RastExtMod
import  CM_intern.CEDM.modules.higherRes as hr        # import HighRes
#import  CEDM.modules.query as qu
#import  CEDM.modules.rasterize as ra
import  CM_intern.common_modules.readCsvData as RCD

#import common_modules.array2raster as a2r
import CM_intern.CEDM.modules.cyf.SumOfHighRes as SOHR
import CM_intern.CEDM.modules.cyf.create_density_map as CDM
#import CEDM.modules.cyf.create_density_map_py as CDMpy
#import CEDM.modules.cyf.SumOfHighRes_py as SOHRpy
import CM_intern.common_modules.cliprasterlayer as CRL

from CM_intern.common_modules.exportLayerDict import export_layer as expLyr
from CM_intern.CEDM.modules.createIndexRasterMap import createIndexMap 

import CM_intern.CEDM.modules.DistrCSVDataToMap as DCSV2Map


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



del_temp_path    = False
process_cut_pop_layer = True
process1           = True
process1a          = True
process2           = True
process3           = True
process4         = True
processOSM = True
   
process_cut_pop_layer = False
process1           = False
process1a          = False
process2           = False
process3           = False
process4         = False
processOSM = False     
 
fp = open('memory_profiler.log', 'w+') 
#sys.stdout = open("print_output.txt", "w")


def _process3(density_indicator, RESOLUTION = 10):
    
    # Create Distribution function of soilsailing (100x100 m) corrected by CLC data 
    # within each  population grid cell (1 km2)
    
    st1 = time.time()
    # Calculate Sum per initial Popgrid
    (data_SS_CLC_1_km) = SOHR.CalcLowResSum(density_indicator, RESOLUTION)

    print("Calc SumLowRes: %4.1f sec " %(time.time() - st1))
    
    
    st1 = time.time()
    #Transfer to high Resolution again 
    data_SS_CLC = SOHR.CalcHighRes(data_SS_CLC_1_km, RESOLUTION) + 10 ** - 4
    
    
    # distribution of high Resolution data within low Resolution 
    rel_density_indicator = density_indicator / data_SS_CLC
    print("Calc CalcHighRes: %4.1f sec " %(time.time() - st1))

    return rel_density_indicator



class ClassCalcPOPULATION():
    
    def __init__(self, prj_path, prj_path_inputraw_data, prj_path_output, preproccessed_input_path):
        
        #Raise error if Data path doesn't exist
        print("Project Path: %s" % os.path.abspath(prj_path))
        if not os.path.exists(prj_path):
            print("Project Path doesn't exist")
        
        assert(os.path.exists(prj_path))
        self.prj_path = prj_path
        
        # Input data path 
        raw_data_path = prj_path  + os.sep + prj_path_inputraw_data 
        
        preprocessed_data_path = prj_path  + os.sep + preproccessed_input_path 
        if not os.path.exists(raw_data_path):
            print("Input data path doesn't exist : %s" % raw_data_path)
        
        self.raw_data_path = raw_data_path
        
        # final output path      
        self.prj_path_output    = "%s/%s" %(prj_path, prj_path_output)  
        
        # Path containing processed Data
        self.proc_data_path    = self.prj_path_output  + os.sep + "Processed Data"    
        # Path containing temporal Data
        self.temp_path        = self.prj_path_output  + os.sep + "Temp"
        
        #create if doesn't exist
        if not os.path.exists(self.proc_data_path):
            os.makedirs(self.proc_data_path)
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        
        
        #self.pixelWidth = 100
        #self.pixelHeight = -100 
        
        # input data files
        # Standard Vector layer (Nuts 3 and LAU shape file)
        self.NUTS3_vector_path = self.raw_data_path + "/vector_input_data/NUTS3.shp"
        self.LAU2_vector_path = self.raw_data_path + "/vector_input_data/Communal2.shp"
        
        self.NUTS_id_number =  preprocessed_data_path + "/NUTS3_id_number.tif"
        self.LAU2_id_number =  preprocessed_data_path + "/LAU2_id_number.tif"
        # Standard raster Layer
        self.strd_raster_path_full = "%s/%s" %(self.raw_data_path, "Population.tif")
        # Population Layer
        self.pop_raster_path_full = "%s/%s" %(self.raw_data_path, "Population.tif")
        self.JRC_POP250_1km_raster_path = "%s/%s" %(self.raw_data_path, "GHS_POP_250_small_3035_new_1km.tif")
        
        self.SoilSeal_path_full = "%s/%s" %(self.raw_data_path, "_____ESM100m_final.tif")
        self.Corine_path_full = "%s/%s" %(self.raw_data_path, "g100_clc12_V18_5.tif")

        # Input Data to be distributed
        self.csv_input_data_LAU2_path = "%s/%s" %(raw_data_path, "Communal2_data_unique.csv")
        self.csv_input_data_NUTS3_path = "%s/%s" %(raw_data_path, "NUTS3_data.csv")
        
        
        
        
        
        # Clipped Raster layer
        self.pop_raster_path = "%s/%s" %(self.temp_path, "Population_clipped.tif")
        self.pop_raster_100m_path = "%s/%s" %(self.temp_path, "Population_100M_clipped.tif")
        self.SoilSeal_path   = "%s/%s" %(self.temp_path, "SS2012_clipped.tif")
        self.Corine_path = "%s/%s" %(self.temp_path, "g100_clc12_V18_5_clipped.tif")
        self.Corine_share_path = "%s/%s" %(self.temp_path, "Corine_share_clipped.tif")
        self.Corine_share_path_POP_weight = "%s/%s" %(self.temp_path, "Corine_POPweight_clipped.tif")
        self.density_function_per_PopGrid = "%s/density_within_pop_grid.pk" %self.temp_path 
        self.CorineSoilSeal_share_path = "%s/%s" %(self.temp_path, "CLC_SoilSeal_share_clipped.tif")
        
        self.NUTS3_cut_vector_path =  self.temp_path + "/NUTS3_cut.shp"
        self.LAU2_cut_vector_path =  self.temp_path + "/LAU2_cut.shp"
        self.NUTS_cut_id_number =  self.temp_path + "/NUTS3_cut_id_number.tif"
        self.LAU2_cut_id_number =  self.temp_path + "/LAU2_cut_id_number.tif"
        
        #outputs
        self.MOST_RECENT_CUT = "%s/MOST_RECENT_CUT.pk" %self.prj_path_output 

        
        
        
      
        # array2raster output datatype
        self.datatype_int = 'uint32'
        #self.datatype_int16 = 'uint16'
        self.datatype = "float32"
        # common parameters
        self.noDataValue = 0
          
    #@profile(stream=fp)     
    def main_process(self, NUTS3_feat_id_LIST):
        
        
        
        
        start_time = time.time()
        
        if del_temp_path:    
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)   
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)    

        
        SaveLayerDict = {}
        # Load Raster Reference Layer
        (REFERENCE_RasterResolution, HighRes_gt_obj, self.LOAD_DATA_PREVIOUS) = \
                self.load_reference_raster_lyr(self.NUTS3_vector_path,
                                               self.strd_raster_path_full, 
                                               self.temp_path, NUTS3_feat_id_LIST)
                
        #######################################
        #
        # Create raster Map (Array) which contains NUTS ID Number  
        #
        #######################################
        
        st = time.time()
        print("\nLOAD INDEX MAPS for NUTS3 and LAU2")
        
        
        OutPutRasterPathNuts = self.NUTS_cut_id_number
        OutPutRasterPathLau2 = self.LAU2_cut_id_number
        dataType16 = 'uint16'
        dataType32 = self.datatype_int
        create_new = True
        if (self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPathNuts) == True
                and os.path.exists(OutPutRasterPathLau2) == True):
            create_new = False
            try:
                
                ARR_LAU2_ID_NUMBER, geotransform_obj = SF.rrl(OutPutRasterPathLau2, data_type=dataType32)
                ARR_NUTS_ID_NUMBER, geotransform_obj = SF.rrl(OutPutRasterPathNuts, data_type=dataType16)
            except:
                create_new = True
        
        ResIncreaseFactor = REFERENCE_RasterResolution / TARGET_RESOLUTION
        
        if create_new == True:   
            if (os.path.exists(self.NUTS_id_number) == True
                    and os.path.exists(self.LAU2_id_number) == True
                    and os.path.getmtime(self.LAU2_vector_path) < os.path.getmtime(self.NUTS_id_number)
                    and os.path.getmtime(self.LAU2_vector_path) < os.path.getmtime(self.LAU2_id_number)):
                
                # The fully extended map exists already and is recent
                # Therefore just load and clip to the desired extent
                ARR_NUTS_ID_NUMBER, geotransform_obj = CRL.clip_raster_layer(self.NUTS_id_number
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)  
                ARR_LAU2_ID_NUMBER, geotransform_obj = CRL.clip_raster_layer(self.LAU2_id_number
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)  
                
            else:    
                print("CREATE NUTS_ID_NUMBER and LAU2_ID_NUMBER MAP first")
            SaveLayerDict["NUTS_ID_NUMBER"] =   [OutPutRasterPathNuts, geotransform_obj
                                                      , dataType16
                                                      , ARR_NUTS_ID_NUMBER , self.noDataValue]
            SaveLayerDict["LAU2_ID_NUMBER"] =   [OutPutRasterPathLau2, geotransform_obj
                                                  , dataType32
                                                  , ARR_LAU2_ID_NUMBER , self.noDataValue]
            

      
        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
                
            elapsed_time = time.time() - st
            print("Process Create INDEX MAPS took: %4.1f seconds" %elapsed_time)
        
        
    
    
        ADD_ID_MAP = {} 
        ADD_ID_MAP["LAU2_ID_NUMBER"] = ARR_LAU2_ID_NUMBER
        ADD_ID_MAP["NUTS_ID_NUMBER"] = ARR_NUTS_ID_NUMBER   
        
        """
        At this stage, only the following ha-Maps are required:
                ARR_LAU2_ID_NUMBER: int32
                ARR_NUTS_ID_NUMBER: uint16     
        """

        #######################################
        #
        # Cut population raster   
        #
        #######################################
        print("\nProcess 0 Population")
        
        FullRasterPath = self.pop_raster_path_full
        
        OutPutRasterPath = self.pop_raster_path
        data_type = self.datatype_int
        
        create_new = True
        if (process_cut_pop_layer == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPath) == True):
            
            create_new = False
            try:
                arr_pop_cut, geotransform_obj_1km = SF.rrl(OutPutRasterPath, data_type=data_type)
            except Exception as e:
                print("Canot import %s"%self.pop_raster_path)
                print(e)
                create_new = True
                
        if 1==1 or create_new == True:
            arr_pop_cut, geotransform_obj_1km = CRL.clip_raster_layer(FullRasterPath
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   

            # Load JRC Population Raster (JRC POP 250m Raster transformed to 1km)
            arr_JRC_pop_cut, geotransform_obj_1km = CRL.clip_raster_layer(self.JRC_POP250_1km_raster_path
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   
            
            #for pixel for with arr_pop_cut Matrix == Zero -> add 30% the value of the JRC Population Map
            EMPTY_MATRIX = np.zeros_like(arr_JRC_pop_cut)
            idxM = arr_pop_cut == 0
            # Add only 30% of value, because adding population if the data 
            # between JRC and main Layer are shifted (which is the case)
            # creates a distortion towards low densely populated areas
            EMPTY_MATRIX[idxM] = 0.3 * arr_JRC_pop_cut[idxM]
            EMPTY_MATRIX[EMPTY_MATRIX < 3] = 0
            EMPTY_MATRIX[EMPTY_MATRIX > 20000] = 20000
            
            """(arr_pop100_no_av, geotransform_obj) = hr.HighResArray(arr_pop_cut
                                , ResIncreaseFactor, geotransform_obj_1km)   
            arr_pop100_no_av = arr_pop100_no_av / ResIncreaseFactor ** 2
            TABLE_LAU_O = CDM.CreateResultsTableperIndicator(arr_pop100_no_av, ARR_LAU2_ID_NUMBER)
            TABLE_NUTS_O = CDM.CreateResultsTableperIndicator(arr_pop100_no_av, ARR_NUTS_ID_NUMBER)
            """   
            arr_pop_cut += EMPTY_MATRIX.astype(self.datatype_int)
            
            SaveLayerDict["population_raster"] =   [OutPutRasterPath, geotransform_obj_1km
                                                  , data_type
                                                  , arr_pop_cut , self.noDataValue]
        
        
        
        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
                
            elapsed_time = time.time() - st
            print("Process 4 took: %4.1f seconds" %elapsed_time)
        
        #######################################
        #
        #End Cut population raster   
        #
        #######################################
        print("Preparation (Clip initial raster file) took: %4.1f " %(time.time() - start_time))
    
    
        #######################################
        #
        # Corine Landcover raster   
        #
        #######################################
        print("\nProcess 1a Corine Landcover data")
        st = time.time()
        
        FullRasterPath = self.Corine_path_full
        OutPutRasterPath = self.Corine_share_path
        OutPutRasterPath_POP_weight = self.Corine_share_path_POP_weight
        data_type = self.datatype
        
        create_new = True
        if (process1a == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPath) == True):
            
            create_new = False
            try:
                arr_corine_share, geotransform_obj = SF.rrl(OutPutRasterPath, data_type=data_type)
                POPweight_corineLC, geotransform_obj = SF.rrl(OutPutRasterPath_POP_weight, data_type=data_type)
            except:
                create_new = True
                
        if create_new == True:
            # cuts Corince Land Cover to same size as REFERENCE layer
            # Save as raster layer
            
            arr_corine_cut, geotransform_obj = CRL.clip_raster_layer(FullRasterPath
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   

            # Transform CLC Code to Building shares
            arr_corine_share = (CORINE_LANDCOVER_TRANSFORM_MATRIX[arr_corine_cut])
            POPweight_corineLC = (CORINE_LANDCOVER_POPWeight[arr_corine_cut])
            
            
            if DEBUG == True:   
                SaveLayerDict["corine_raster"] =   [self.Corine_path, geotransform_obj
                                                  , self.datatype_int
                                                  , arr_corine_cut , self.noDataValue]
                SaveLayerDict = expLyr(SaveLayerDict)
            
            del arr_corine_cut
                
            SaveLayerDict["corine_share_raster"] =   [OutPutRasterPath, geotransform_obj
                                                  , data_type
                                                  , arr_corine_share, self.noDataValue]
            SaveLayerDict["corine_pop_weight_raster"] =   [OutPutRasterPath_POP_weight, geotransform_obj
                                                  , data_type
                                                  , POPweight_corineLC, self.noDataValue]
           
        elapsed_time = time.time() - st
        
        print("Process 1a: Cut and Calc Corine Shares took: %4.1f seconds" %elapsed_time)
        #######################################
        #
        # End Corine Landcover raster   
        #
        #######################################
        SaveLayerDict = expLyr(SaveLayerDict)
         
        """
        At this stage, only the following ha-Maps are required:
                ARR_LAU2_ID_NUMBER: int32
                ARR_NUTS_ID_NUMBER: uint16  
                POPweight_corineLC: float32
                arr_corine_share: float32                   
        """
        
        
        #######################################
        #
        # Transform POPUlation Layer to 100 meter raster   
        #
        #######################################
        
        print("\nProcess 2: Transform Population layer to %i Meter Raster" % TARGET_RESOLUTION)
        st = time.time()
        create_new = True
        
        OutPutRasterPath = self.pop_raster_100m_path
        data_type = self.datatype
        
        if (process2 == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPath) == True):
            
            create_new = False
            try:
                ARR_POPULATION_100, geotransform_obj = SF.rrl(OutPutRasterPath, data_type=data_type)
                arr_pop100_1km, geotransform_obj = SF.rrl("%s_100_1km.tif" %OutPutRasterPath[:-4], data_type=data_type)
            except:
                create_new = True
                
        if create_new == True:
            # cuts SOIL Sealing cuts to same size as REFERENCE layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            
            
            
            (arr_pop100_no_av, geotransform_obj) = hr.HighResArray(arr_pop_cut
                                , ResIncreaseFactor, geotransform_obj_1km)
            
            arr_pop100_1km = arr_pop100_no_av.copy() + 0.0001
            arr_pop100_no_av = arr_pop100_no_av.astype(data_type) / ResIncreaseFactor ** 2
    
            SaveLayerDict["data_pop100_1km"] = ("%s_100_1km.tif" %OutPutRasterPath[:-4]
                                        , geotransform_obj
                                        , data_type, arr_pop100_1km , self.noDataValue)
            
            
            print ("HighRes took: %4.2f sec " % (time.time()-st))
            st1 = time.time()
            print (np.sum(arr_pop100_no_av)) 
            if DEBUG == True:
                print (np.sum(arr_pop100_no_av)) 
                SaveLayerDict["data_pop100_no_average"] = ("%s_before" %OutPutRasterPath
                                        , geotransform_obj
                                        , data_type, arr_pop100_no_av , self.noDataValue)
                SaveLayerDict = expLyr(SaveLayerDict)
                
            ARR_POPULATION_100 = SOHR.CalcAverageBased(arr_pop100_no_av, 10, 6, 1
                                                       , POPweight_corineLC)
            
            del POPweight_corineLC
            del arr_pop100_no_av #no impact(?) Memory is still needed for ARR_POPULATION_100!
            
            print ("CalcAverageBased took: %4.2f sec " % (time.time()-st1))
            
            SaveLayerDict["data_pop100"] = (OutPutRasterPath, geotransform_obj
                                        , data_type, ARR_POPULATION_100 , self.noDataValue)
        else:
            del POPweight_corineLC
            
        self.geotransform_obj_high_res = geotransform_obj 
        self.arr_size_high_res = ARR_POPULATION_100.shape 
        elapsed_time = time.time() - st
        print("Process 2 took: %4.1f seconds" %elapsed_time)
        #######################################
        #
        # End Transform POPUlation Layer to 100 meter raster   
        #
        #######################################
        
            
        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
        
        """
        At this stage, the following ha-Maps are required:
                ARR_NUTS_ID_NUMBER: uint16  
                ARR_LAU2_ID_NUMBER: int32
                arr_corine_share: float32 
                ARR_POPULATION_100: float32 
                arr_pop100_1km: float32                     
        """
        
        #######################################
        #
        # Cut Soil Sealing raster   
        #
        #######################################
        print("\nProcess 1 SoilSealing")
        st = time.time()
        create_new = True
        
        FullRasterPath = self.SoilSeal_path_full
        OutPutRasterPath = self.SoilSeal_path
        data_type = "float32"
        
        if (process1 == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPath) == True):
            
            create_new = False
            try:
                arr_soilseal_cut, geotransform_obj = SF.rrl(OutPutRasterPath, data_type=data_type)
            except:
                create_new = True
                
        if create_new == True:
            # cuts SOIL Sealing cuts to same size as REFERENCE layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            
            arr_soilseal_cut, geotransform_obj = CRL.clip_raster_layer(FullRasterPath
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   

        
            arr_soilseal_cut = np.maximum(0, arr_soilseal_cut)
            arr_soilseal_cut = np.minimum(100, arr_soilseal_cut)
                

        SaveLayerDict["soilseal_raster"] =   [OutPutRasterPath, geotransform_obj
                                                  , data_type
                                                  , arr_soilseal_cut , self.noDataValue]
           
        elapsed_time = time.time() - st
        
        print("Process 1: Cut SoilSealing took: %4.1f seconds" %elapsed_time)
        #######################################
        #
        # End Cut Soil Sealing raster   
        #
        #######################################
        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
        
        """
        At this stage, the following ha-Maps are required:
                ARR_NUTS_ID_NUMBER: uint16  
                ARR_LAU2_ID_NUMBER: int32
                arr_corine_share: float32 
                ARR_POPULATION_100: float32 
                arr_pop100_1km: float32  
                arr_soilseal_cut: float32                   
        """
        
        
        
        #######################################
        #
        # Calculate Distribution function within each population grid cell   
        #
        #######################################
        # Calculate the relative shares of SoilSealingxCorineLandCover Distribution [100m2] within 
        # original Population Raster [1km2]
        print("\nProcess 3 Create Density within Population Grid")
        st = time.time()
        

        OutPutRasterPath = self.density_function_per_PopGrid 
        data_type = self.datatype
        
        create_new = True
        if (process3 == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(OutPutRasterPath) == True):
            
            create_new = False
            try:
                RelativeDensityDistributionWithinPopRaster, geotransform_obj = SF.rrl(OutPutRasterPath, data_type=data_type)
            except:
                create_new = True
                
        if create_new == True:
            density_indicator = arr_corine_share * arr_soilseal_cut / 100.0
            
           
            #ResIncreaseFactor = PopulationRasterResolution / TARGET_RESOLUTION
            RelativeDensityDistributionWithinPopRaster = _process3(density_indicator, ResIncreaseFactor)
            
            if DEBUG == True:
                SaveLayerDict["density_indicator"] =   [self.CorineSoilSeal_share_path, geotransform_obj
                                                  , data_type
                                                  , density_indicator , self.noDataValue]
                
            SaveLayerDict["relative_density_indicator"] =   [OutPutRasterPath, geotransform_obj
                                                  , data_type
                                                  , RelativeDensityDistributionWithinPopRaster
                                                  , self.noDataValue]

            SaveLayerDict = expLyr(SaveLayerDict)
            del density_indicator  
        del arr_corine_share
        DENSITY_INDICATOR_MAP_POP = (RelativeDensityDistributionWithinPopRaster 
                                      * ARR_POPULATION_100)
        
        DENSITY_INDICATOR_MAP_POP_1km = SOHR.CalcLowResSum(DENSITY_INDICATOR_MAP_POP, ResIncreaseFactor)
        
        Ratio = (arr_pop_cut + 0.1 ) / (DENSITY_INDICATOR_MAP_POP_1km + 0.1 )

        Ratio = np.maximum(0.5, np.minimum(10000, Ratio))
        Ratio_100m =  SOHR.CalcHighRes(Ratio, ResIncreaseFactor)   
        DENSITY_INDICATOR_MAP_POP *= Ratio_100m
        
        
        SaveLayerDict["DENSITY_INDICATOR_MAP_POP"] =   ["%s/%s.tif" %(self.temp_path, "__DENSITY_INDICATOR_MAP_POP"), geotransform_obj
                                                  , data_type
                                                  , DENSITY_INDICATOR_MAP_POP
                                                  , self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        
        del RelativeDensityDistributionWithinPopRaster, Ratio_100m
        #######################################
        #
        # End: Calculate Distribution function within each population grid cell   
        #
        #######################################
        """
        At this stage, the following ha-Maps are required:
                ARR_NUTS_ID_NUMBER: uint16  
                ARR_LAU2_ID_NUMBER: int32
                arr_corine_share: float32 --> Deleted
                ARR_POPULATION_100: float32 
                arr_pop100_1km: float32  
                arr_soilseal_cut: float32    
                DENSITY_INDICATOR_MAP_POP: float32               
        """
        print("\n\n\n######\n\nProcess took: %4.1f seconds so far\n\n\n" %(time.time() - start_time))
        #######################################
        #
        # LOAD CSV DATA on POPULATION per LAU region
        # And correct data for LAU and RASTER 
        # Modifies:
        #     DENSITY_INDICATOR_MAP_POP
        #
        #######################################
        if "noLAUcorr" not in self.temp_path:
            
            (LAU_DATA, EXPORT_COLUMNS
            , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_input_data_LAU2_path)
            A= np.zeros(LAU_DATA['POP_2012'].shape[0], dtype="f4")
            A[0:] =LAU_DATA['POP_2012']
            
            print(np.max(DENSITY_INDICATOR_MAP_POP))
            TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_INDICATOR_MAP_POP, ARR_LAU2_ID_NUMBER)   
            
            
            num_run = 1
            TAB_res = np.zeros((TABLE_RESULTS.shape[0], 2+num_run))
            
            TAB_res[:,:2] = TABLE_RESULTS
    
            max_pop = self.calc_max_pop(arr_pop100_1km)
            for ii in range(num_run):
                print("########\nRun %i" %ii)
                # limit population per hectare
                DENSITY_INDICATOR_MAP_POP = np.minimum(DENSITY_INDICATOR_MAP_POP, max_pop)
                #print(np.sum(DENSITY_INDICATOR_MAP_POP))
                DENSITY_INDICATOR_MAP_POP = CDM.ScaleResultsWithTableperIndicator(DENSITY_INDICATOR_MAP_POP
                                                        , ARR_LAU2_ID_NUMBER, A, 
                                                        elasticitiy = 0.66, maxscale = 1.3)
                #print(np.sum(DENSITY_INDICATOR_MAP_POP))
                """
                SaveLayerDict["POP_new"] =   ["%s/%s_run_%i.tif" %(self.temp_path, "POP_new_unrestrict", ii), geotransform_obj
                                                      , data_type
                                                      , DENSITY_INDICATOR_MAP_POP , self.noDataValue]
            
                SaveLayerDict = expLyr(SaveLayerDict) 
                """
                DENSITY_INDICATOR_MAP_POP_1km = SOHR.CalcLowResSum(DENSITY_INDICATOR_MAP_POP, ResIncreaseFactor)
                Ratio = ((arr_pop_cut + 0.1 ) / (DENSITY_INDICATOR_MAP_POP_1km + 0.1 )) ** 0.66
                
                #sys.exit()
                #Ratio = np.maximum(0.5, np.minimum(1.5, Ratio))
                Ratio_100m =  SOHR.CalcHighRes(Ratio, ResIncreaseFactor)   
                DENSITY_INDICATOR_MAP_POP *= Ratio_100m
                
                # limit population per hectare
                DENSITY_INDICATOR_MAP_POP = np.minimum(DENSITY_INDICATOR_MAP_POP, max_pop)
                
                
                
                SaveLayerDict["POP_new"] =   ["%s/%s_run_%i.tif" %(self.temp_path, "POP_new", ii), geotransform_obj
                                                      , data_type
                                                      , DENSITY_INDICATOR_MAP_POP , self.noDataValue]
            
                SaveLayerDict = expLyr(SaveLayerDict) 
                
                print(np.max(DENSITY_INDICATOR_MAP_POP))
    
                TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_INDICATOR_MAP_POP, ARR_LAU2_ID_NUMBER)           
                TAB_res[:,ii+2] = TABLE_RESULTS[:, 1]
            
            fn_ = ("%s/%s.csv" %(self.temp_path, "TEST_ARR_POPULATION_LAU_X"))
            np.savetxt(fn_, np.round(TAB_res, 0), delimiter=",")
            
            del DENSITY_INDICATOR_MAP_POP_1km, Ratio, Ratio_100m
        del max_pop, arr_pop100_1km
        #######################################
        #
        # End: Modify GRID POPLUATION (DENSITY_INDICATOR_MAP_POP) based on LAU Population
        #
        #######################################


        SaveLayerDict = expLyr(SaveLayerDict)
        
        print("CALC POPULATION finished")
        
    def calc_max_pop(self, population):
        
        max_pop = population.copy()
        
        idx = population <= 1000
        
        M = max_pop[idx] / 1000
        RES = 0.12 * M ** (1-0.3)* 1000
        max_pop[idx] = RES
        
        idx = np.logical_and(population > 1000, population <= 15000)
        M = max_pop[idx] / 1000
        RES = (0.1276 - 0.0067 * M + 0.0001112 * M * M) * M * 1000
        max_pop[idx] = RES
        
        idx = population > 15000
        M = max_pop[idx]
        RES = (618.5 + 0.0109 * M )
        max_pop[idx] = RES
        
        max_pop = np.maximum(max_pop, 0.02 * population)
        max_pop = np.minimum(max_pop, population)
            
            
        return max_pop
    
    
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
        
        
        if LOAD_DATA_PREVIOUS != True and deletedata == True:
            
            if os.path.exists(self.proc_data_path):
                shutil.rmtree(self.proc_data_path)   
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)
            if os.path.exists(outputpath):
                shutil.rmtree(outputpath)
            
            if not os.path.exists(outputpath):
                os.makedirs(outputpath) 
            if not os.path.exists(self.proc_data_path):
                os.makedirs(self.proc_data_path)
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)
                
                
            with open(filename, 'wb') as fobject:
                pickle.dump(REFERENCE_RASTER_LAYER_COORD, fobject, protocol=2)
                fobject.close()
        SaveLayerDict = expLyr(SaveLayerDict)
        
        return (REFERENCE_RasterResolution, HighRes_gt_obj, LOAD_DATA_PREVIOUS)