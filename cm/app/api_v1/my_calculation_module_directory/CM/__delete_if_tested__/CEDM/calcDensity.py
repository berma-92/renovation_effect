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

#@profile
def _process_final_density_map(output_path, noDataValue
              , density_indicator_map, geotransform_Object
              , NUTS_ID_MAP
              , OSM_BGF
              , OSM_DataWeight
              , POP_Weight
              , POSTFIX_fn=""):
    
    SaveLayerDict = {}
    #print("Process 5")
    
    datatype = "float32"
    
    st1 = time.time()
    DENSITY_MAP_POP = CDM.CreateDensistyMap(density_indicator_map, NUTS_ID_MAP)
    
    if type(DENSITY_MAP_POP).__name__ != 'ndarray':
        sys.exit()
    
    if DEBUG:
        filename = "DENSITY_MAP_POP_based_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , DENSITY_MAP_POP, noDataValue)
    
        SaveLayerDict = expLyr(SaveLayerDict)
        TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP_POP, NUTS_ID_MAP)   
        np.savetxt("%s/%s.csv" %(output_path, filename), np.round(TABLE_RESULTS, 0), delimiter=",")
        
    print ("CreateDensistyMap POP based took: %5.1f sec" % (time.time() - st1)) 
    
    DENSITY_MAP_OSM = CDM.CreateDensistyMap(OSM_BGF, NUTS_ID_MAP)
    
    del OSM_BGF
    if type(DENSITY_MAP_OSM).__name__ != 'ndarray':
        sys.exit()
    
    if DEBUG:
        filename = "DENSITY_MAP_OSM_based_%s" % POSTFIX_fn
        SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                        , geotransform_Object
                        , datatype
                        , DENSITY_MAP_OSM, noDataValue)
        TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP_OSM, NUTS_ID_MAP)   
        np.savetxt("%s/%s.csv" %(output_path, filename), np.round(TABLE_RESULTS, 0), delimiter=",")
    
        if type(OSM_DataWeight) is not float and type(OSM_DataWeight) is not int:
            filename = "DENSITY_MAP_OSM_Weight_%s" % POSTFIX_fn
            SaveLayerDict[filename] = ("%s/%s.tif" %(output_path, filename)
                            , geotransform_Object
                            , datatype
                            , OSM_DataWeight, noDataValue)
        if type(POP_Weight) is not float and type(POP_Weight) is not int:
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
    
    DENSITY_MAP = CDM.CreateDensistyMap(combined_density_indicator_map, NUTS_ID_MAP)
    TABLE_RESULTS = CDM.CreateResultsTableperIndicator(DENSITY_MAP, NUTS_ID_MAP)   
    np.savetxt("%s/%s.csv" %(output_path, "DENSITY_MAP_combined_%s" % POSTFIX_fn), np.round(TABLE_RESULTS, 0), delimiter=",")
    
    
    print ("CreateDensistyMap took: %5.1f sec" % (time.time() - st1))
    return DENSITY_MAP



class ClassCalcDensity():
    
    def __init__(self, prj_path, prj_path_input, prj_path_output
                 , preproccessed_input_path):
        
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
        self.preproccessed_input_data = "%s/%s/" %(prj_path, preproccessed_input_path)
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
        self.NUTS3_vector_path = self.org_data_path + "/vector_input_data/NUTS3.shp"
        self.LAU2_vector_path = self.org_data_path + "/vector_input_data/Communal2.shp"
        self.NUTS_id_number =  self.preproccessed_input_data + "/NUTS3_id_number.tif"
        self.LAU2_id_number =  self.preproccessed_input_data + "/LAU2_id_number.tif"
        # Standard raster Layer
        self.strd_raster_path_full = "%s/%s" %(self.org_data_path, "Population.tif")
        # Population Layer
        self.pop_raster_path_full = "%s/%s" %(self.org_data_path, "Population.tif")
        self.JRC_POP250_1km_raster_path = "%s/%s" %(self.org_data_path, "GHS_POP_250_small_3035_new_1km.tif")
        
        self.SoilSeal_path_full = "%s/%s" %(self.org_data_path, "_____ESM100m_final.tif")
        self.Corine_path_full = "%s/%s" %(self.org_data_path, "g100_clc12_V18_5.tif")
        
        self.OSMBGF_path_full = "%s/%s" %(self.preproccessed_input_data, "_____3__FINAL_OSMbuildings_GFA.tif")
        self.Surface_Volumne_basedEnergyIntensity_fn_path = "%s/_____5__FINAL_OSMbuildings_S_GFA_ratio_corr.tif" % self.preproccessed_input_data
        self.OSMBFP_path_full = "%s/%s" %(self.preproccessed_input_data, "_____0__FINAL_OSMbuildings_FOOTPRINT.tif")
        
        self.CPbasedEnergyIntensity_fn_path = "%s/SoilSeal_ConstrPeriods/CPbased_EnergyIntensity.tif" % self.preproccessed_input_data  
        self.HDDbasedEnergyIntensity_fn_path = "%s/HDD_CDD_data_new/HDD_EnergyIntensityIndicator.tif" % (self.preproccessed_input_data) 


        # Input Data to be distributed
        self.csv_input_data_LAU2_path = "%s/%s" %(org_data_path, "Communal2_data_unique.csv")
        self.csv_input_data_NUTS3_path = "%s/%s" %(org_data_path, "NUTS3_data.csv")
        
        
        
        
        
        # Clipped Raster layer
        self.pop_raster_path = "%s/%s" %(self.temp_path, "Population_clipped.tif")
        self.pop_raster_100m_path = "%s/%s" %(self.temp_path, "Population_100M_clipped.tif")
        self.SoilSeal_path   = "%s/%s" %(self.temp_path, "SS2012_clipped.tif")
        self.Corine_path = "%s/%s" %(self.temp_path, "g100_clc12_V18_5_clipped.tif")
        self.Corine_share_path = "%s/%s" %(self.temp_path, "Corine_share_clipped.tif")
        self.Corine_share_path_POP_weight = "%s/%s" %(self.temp_path, "Corine_POPweight_clipped.tif")
        self.density_function_per_PopGrid = "%s/density_within_pop_grid.pk" %self.temp_path 
        self.CorineSoilSeal_share_path = "%s/%s" %(self.temp_path, "CLC_SoilSeal_share_clipped.tif")
        
        self.OSMBGF_path_cut = "%s/%s" %(self.temp_path, "OSMbuildings_FOOTPRINT_clipped.tif")
        
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
        print("\nCreate INDEX MAPS for NUTS3 and LAU2")
        
        
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
                ARR_size_high_res = []
                ARR_size_high_res.append(int(self.REFERENCE_RasterSize[0] * ResIncreaseFactor))
                ARR_size_high_res.append(int(self.REFERENCE_RasterSize[1] * ResIncreaseFactor))
                #Create Rasterfile with NUTS ID for each pixel
                ARR_NUTS_ID_NUMBER, geotransform_obj  = createIndexMap(self.NUTS3_vector_path
                                            , self.NUTS3_cut_vector_path, self.REFERENCE_extent
                                           , HighRes_gt_obj
                                           , ARR_size_high_res
                                           , self.noDataValue
                                           , dataType16
                                           , key_field = "NUTS_ID"
                                           , value_field = "IDNUMBER"
                                           , out_field_name = "IDNUMBER")
                
                
              
                #Create Rasterfile with LAU2 ID for each pixel
                ARR_LAU2_ID_NUMBER, geotransform_obj  = createIndexMap(self.LAU2_vector_path
                                            , self.LAU2_cut_vector_path, self.REFERENCE_extent
                                           , HighRes_gt_obj
                                           , ARR_size_high_res
                                           , self.noDataValue
                                           , dataType32
                                           , key_field = "COMM_ID"
                                           , value_field = "LAU_UDATAI"
                                           , out_field_name = "LAU_UDATAI")
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
        # CREATE ENERGY INTENSITY MATRIX 
        # Creates:
        #     ConstPeriodBasedEnergyIntensity
        #
        #######################################
             
        create_new = True
        filename = "EnergyIntensity_CP_Surf_Vol_HDD_ratio"
        
        
        density_map_energy_intensity_fn = ("%s/%s.tif" %(self.temp_path, filename))
        
        data_type = self.datatype
        if (self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(density_map_energy_intensity_fn) == True):
            
            create_new = False
            try:
                pass
                #ConstPeriodBasedEnergyIntensity, geotransform_obj = SF.rrl(density_map_energy_intensity_fn, data_type=data_type)
                #del ConstPeriodBasedEnergyIntensity
            except:
                create_new = True   
        if create_new == True: 
            #Calculate and store on Disk 
            self.calc_EnergyIntensity_CP_Surf_Vol_HDD_ratio(density_map_energy_intensity_fn)   
            
        #######################################
        #
        # END OF: CREATE ENERGY INTENSITY MATRIX 
        #
        #######################################
        
        
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

        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
        
        #######################################
        #
        # CALC preliminary Value added and non-res m2 resulting from Value added
        #
        #######################################
        
        (LAU_DATA, EXPORT_COLUMNS
            , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_input_data_LAU2_path)
        A = np.zeros(LAU_DATA['VAperCap'].shape[0], dtype="f4")
        A[0:] = LAU_DATA['VAperCap']

        SPECIFIC_VAperPOP = A[ARR_LAU2_ID_NUMBER]
        VA = np.zeros_like(ARR_POPULATION_100)
        VA[:,:] = SPECIFIC_VAperPOP * ARR_POPULATION_100 
        BGF_nRES_min = VA 
        (NUTS_DATA, EXPORT_COLUMNS
            , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_input_data_NUTS3_path)
        
        A = np.zeros(NUTS_DATA['m2_per_tdsGDP'].shape[0], dtype="f4")
        A[0:] = NUTS_DATA['m2_per_tdsGDP']
        A = (0.30 ) * np.minimum(5, A) #(At least 30 % of NUTS average is required)
        # A[ARR_NUTS_ID_NUMBER] => specific_nRES_GFA
        BGF_nRES_min *= A[ARR_NUTS_ID_NUMBER]   
        SaveLayerDict["___BGF_nRES_min"] =   [("%s/%s.tif" %(self.temp_path, "___BGF_nRES_min"))
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , BGF_nRES_min, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        del VA, SPECIFIC_VAperPOP
        del A
        #######################################
        #
        # END of CALC preliminary Value added and non-res m2
        #
        #######################################    
        del ARR_POPULATION_100
        """
        At this stage, the following ha-Maps are required:
                ARR_NUTS_ID_NUMBER: uint16  
                ARR_LAU2_ID_NUMBER: int32
                arr_soilseal_cut: float32    
                DENSITY_INDICATOR_MAP_POP: float32  
                BGF_nRES_min: float32             
        """
        print("\n\n\n######\n\nProcess took: %4.1f seconds so far\n\n\n" %(time.time() - start_time))


        #######################################
        #
        # LOAD OSM DATA AND CALC AVERAGE BGF per inhabitant
        # Evaluate the data quality of the OSM dataset  
        # 
        #
        #######################################
        st = time.time()
        print("\nProcess OSM")
        
        
        OSM_GFA_per_Inhab = "%s/%s" %(self.temp_path, "OSM_GFA_per_Inhab_clipped.tif")

        #dataType = self.datatype
        

        filename = "TEST_OSM_QUALITY_DENSITY_MAP_POP_final"
        density_map_pop_OSMbased_fn = ("%s/%s.tif" %(self.temp_path, filename))
        filename = "DENSITY_MAP_POP_final"
        density_map_pop_fn = ("%s/%s.tif" %(self.temp_path, filename))
        filename = "DENSITY_MAP_RES_ENERGY_final"
        density_map_res_energy_fn = ("%s/%s.tif" %(self.temp_path, filename))
        
        DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn = "%s/DENSITY_INDICATOR_MAP_OSM_BGF.tif" %(self.temp_path)
        OSM_DataQuality_corr_high_RES_output_fn = "%s/OSM_DataQuality_corr_high_RES.tif" %(self.temp_path)

        
        create_new = True
        if (processOSM == False 
                and self.LOAD_DATA_PREVIOUS == True 
                and os.path.exists(DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn) == True
                and os.path.exists(OSM_DataQuality_corr_high_RES_output_fn) == True):
            
            create_new = False
            try:
                DENSITY_INDICATOR_MAP_OSM_BGF, geotransform_obj = SF.rrl(DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn, data_type=data_type)
                OSM_DataQuality_corr_high_RES, geotransform_obj = SF.rrl(OSM_DataQuality_corr_high_RES_output_fn, data_type=data_type)
            except:
                create_new = True   
        create_new = True   
        if create_new == True:  
            (DENSITY_INDICATOR_MAP_OSM_BGF
                , OSM_DataQuality_corr_high_RES) = self.calc_OSM_LAYER(self.OSMBGF_path_full
                                                        , self.OSMBFP_path_full
                                                        , self.OSMBGF_path_cut
                                                        , ResIncreaseFactor
                                                        , OSM_GFA_per_Inhab
                                                        , arr_soilseal_cut
                                                        , BGF_nRES_min
                                                        , arr_pop_cut
                                                        , ARR_NUTS_ID_NUMBER
                                                        , DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn
                                                        , OSM_DataQuality_corr_high_RES_output_fn)
            
            
        try:
            del arr_soilseal_cut, BGF_nRES_min, arr_pop_cut
        except:
            pass
  
          
        """
        At this stage, the following ha-Maps are required:
                ARR_NUTS_ID_NUMBER: uint16  
                ARR_LAU2_ID_NUMBER: int32
                DENSITY_INDICATOR_MAP_POP: float32 
                OSM_DataQuality_corr_high_RES: float32 
                DENSITY_INDICATOR_MAP_OSM_BGF: float32               
        """
        print("\n\n\n######\n\nProcess took: %4.1f seconds so far\n\n\n" %(time.time() - start_time))
        if 1==1:
            
            csv_input_data_file = self.csv_input_data_NUTS3_path
            
            print("\nProcess 5 - create TEST_OSM_Quality-LAYERS")
            # Test OSM Distribution
            TEST_OSM_Quality_DENSITY_INDICATOR_MAP_POP = _process_final_density_map(self.temp_path, self.noDataValue
                                   , DENSITY_INDICATOR_MAP_POP, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , DENSITY_INDICATOR_MAP_OSM_BGF
                                   , OSM_DataQuality_corr_high_RES
                                   , 0.01
                                   , "POP_related")
            
            SaveLayerDict["TEST_OSM_Quality_DENSITY_INDICATOR_MAP_POP"] =   [density_map_pop_OSMbased_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , TEST_OSM_Quality_DENSITY_INDICATOR_MAP_POP, self.noDataValue]
            
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.temp_path, self.noDataValue
                                       , TEST_OSM_Quality_DENSITY_INDICATOR_MAP_POP
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "POP_"
                                       , ADD_ID_MAP= ADD_ID_MAP
                                       , filename_prefix = "TEST_OSM_Quality_"))
            SaveLayerDict = expLyr(SaveLayerDict)
            del TEST_OSM_Quality_DENSITY_INDICATOR_MAP_POP
            
            #"""
            #######################################
            #
            # Create Final Maps (Array) with Results
            #
            #######################################
            # Density Function of Population
            # Decrease the weighting of the OSM Approach
            
            print("\nProcess 5 - create residential LAYERS") 
            
            st1 = time.time()
            # Create RESIDENTIAL LAYERS
            # POPULATION, DWELLINGS, RES GFA, RES VOLUME, RES ENERGY HEATING
            w = 0.05
            OSM_DataQuality_corr_high_RES *= w
            Final_DENSITY_INDICATOR_MAP_POP = _process_final_density_map(self.temp_path, self.noDataValue
                                   , DENSITY_INDICATOR_MAP_POP, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , DENSITY_INDICATOR_MAP_OSM_BGF
                                   , OSM_DataQuality_corr_high_RES
                                   , 1 
                                   , "POP_related")
            
            SaveLayerDict["Final_DENSITY_INDICATOR_MAPPOP"] =   [density_map_pop_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , Final_DENSITY_INDICATOR_MAP_POP, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
            del OSM_DataQuality_corr_high_RES
            
            # Create Final POPULATION (Array) with Results
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_POP
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "POP_"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            # Create Final Gross Floor Area of Residential buildings (Array) with Results
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_POP
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "GFA_RES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            # Create Final Heated Building Volume of Residential buildings (Array) with Results
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_POP
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "VOL_RES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            SaveLayerDict = expLyr(SaveLayerDict)
            
            
            ####################
            # LOAD: ConstPeriodBasedEnergyIntensity
            ####################
            filename = ("%s/%s.tif" %(self.temp_path, "EnergyIntensity_CP_Surf_Vol_HDD_ratio"))
            ConstPeriodBasedEnergyIntensity, geotransform_obj = SF.rrl(filename, data_type)
            
            DENSITY_INDICATOR_MAP_POP *= ConstPeriodBasedEnergyIntensity
            DENSITY_INDICATOR_MAP_OSM_BGF  *= ConstPeriodBasedEnergyIntensity
            del ConstPeriodBasedEnergyIntensity
            
            OSM_DataQuality_corr_high_RES, geotransform_obj = SF.rrl(OSM_DataQuality_corr_high_RES_output_fn, data_type=data_type)
            
            
            Final_DENSITY_INDICATOR_MAP_RES_Energy = _process_final_density_map(self.temp_path, self.noDataValue
                                   , DENSITY_INDICATOR_MAP_POP, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , DENSITY_INDICATOR_MAP_OSM_BGF
                                   , OSM_DataQuality_corr_high_RES
                                   , 1 
                                   , "POP_related")
            del DENSITY_INDICATOR_MAP_POP, OSM_DataQuality_corr_high_RES
            SaveLayerDict["Final_DENSITY_INDICATOR_MAP_RESE"] =   [density_map_res_energy_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , Final_DENSITY_INDICATOR_MAP_RES_Energy, self.noDataValue]
            # Create Final POPULATION (Array) with Results
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_RES_Energy
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "ENERGY_HEATING_RES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            
            
            
            SaveLayerDict = expLyr(SaveLayerDict)
            del DENSITY_INDICATOR_MAP_OSM_BGF
            del Final_DENSITY_INDICATOR_MAP_RES_Energy, Final_DENSITY_INDICATOR_MAP_POP
         
            # At this stage, all residential layers should be created
               
            """
            At this stage, the following ha-Maps are required:
                    ARR_NUTS_ID_NUMBER: uint16  
                    ARR_LAU2_ID_NUMBER: int32          
            """
            print("\n\n\n######\n\nProcess took: %4.1f seconds so far\n\n\n" %(time.time() - start_time))
            print("CREATE NON-RESIDENTIAL LAYERS")
            print("CREATE GDP LAYERS")
            # Create GDP LAYER
            (LAU_DATA, EXPORT_COLUMNS
            , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_input_data_LAU2_path)
            A = np.zeros(LAU_DATA['VAperCap'].shape[0], dtype="f4")
            A[0:] = LAU_DATA['VAperCap']
            
            
            SPECIFIC_VAperPOP = A[ARR_LAU2_ID_NUMBER]
            fn = "%s/RESULTS_POP_2012.tif" % self.proc_data_path
            print("Read Created Population layer: %s" %fn)
            POPULATION, geotransform_obj = SF.rrl(fn, data_type=data_type) 
            VA = np.zeros_like(POPULATION)
            VA[:,:] = POPULATION 
            VA *= SPECIFIC_VAperPOP
            TABLE_RESULTS = CDM.CreateResultsTableperIndicator(VA, ARR_LAU2_ID_NUMBER)   
            
            fn_ = ("%s/%s.csv" %(self.temp_path, "TEST_VA_per_LAU"))
            np.savetxt(fn_, np.round(TABLE_RESULTS, 1), delimiter=",")
 
            del SPECIFIC_VAperPOP
            filename = "MAP_GDP_final"
            map_gdp_fn = ("%s/%s.tif" %(self.temp_path, filename))
            SaveLayerDict["VA"] =   [map_gdp_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , VA, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
            
            
            print("CREATE GFA-Non Residential Buildings LAYERS:")
            print("Start with density function")

            ####################
            # LOAD: DENSITY_INDICATOR_MAP_OSM_BGF and POPweight_corineLC
            ####################
            fn = DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn
            DENSITY_INDICATOR_MAP_OSM_BGF, geotransform_obj = SF.rrl(fn, data_type=data_type)
            
            fn = self.Corine_share_path_POP_weight
            POPweight_corineLC, geotransform_obj = SF.rrl(fn, data_type=data_type)
            
            fn = OSM_DataQuality_corr_high_RES_output_fn
            OSM_DataQuality_corr_high_RES, geotransform_obj = SF.rrl(fn, data_type=data_type)
                        
            Final_DENSITY_INDICATOR_MAP_GFA_NRES = _process_final_density_map(self.temp_path, self.noDataValue
                                   , VA, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , DENSITY_INDICATOR_MAP_OSM_BGF
                                   , OSM_DataQuality_corr_high_RES
                                   , POPweight_corineLC
                                   , "GFA_NRES_related")
            
            del OSM_DataQuality_corr_high_RES, POPweight_corineLC
            filename = "DENSITY_MAP_GFA_NRES"
            density_map_gfa_nres_fn = ("%s/%s.tif" %(self.temp_path, filename))
            SaveLayerDict["Final_DENSITY_INDICATOR_MAP_GFA_NRES"] =   [density_map_gfa_nres_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , Final_DENSITY_INDICATOR_MAP_GFA_NRES, self.noDataValue]

            print("Create GFA_NRES")
            csv_input_data_file = self.csv_input_data_NUTS3_path
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_GFA_NRES
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "GFA_NRES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            fn = "%s/RESULTS_GFA_NRES_BUILD.tif" % self.proc_data_path
            print("Read Created GFA_NRES_BUILD layer: %s" %fn)
            GFA_NRES_BUILD_orig, geotransform_obj = SF.rrl(fn, data_type=data_type) 
            
            
            SaveLayerDict["POP_GFA_reduction"] =   [("%s/%s.tif" %(self.temp_path, "___POP_GFA_reduction"))
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , (6.3) * POPULATION, self.noDataValue]
            SaveLayerDict["GFA_NRES_BUILD"] =   [("%s/%s.tif" %(self.temp_path, "___GFA_NRES_BUILD_"))
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , GFA_NRES_BUILD_orig, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
            
            GFA_NRES_BUILD = GFA_NRES_BUILD_orig - (6.3) * POPULATION   #6.3: Regression of HRM Europe -> Peta Atlas
            del POPULATION
            filename = "GFA_NRES_BUILD_AFTER_POP_substraction"
            GFA_NRES_BUILD = np.maximum(GFA_NRES_BUILD_orig * 0.4, GFA_NRES_BUILD )
            del GFA_NRES_BUILD_orig
            density_map_gfa_nres_after_pop_fn = ("%s/%s.tif" %(self.temp_path, filename))
            SaveLayerDict["GFA_NRES_BUILD_after_pop"] =   [density_map_gfa_nres_after_pop_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , GFA_NRES_BUILD, self.noDataValue]
            
            Final_DENSITY_INDICATOR_MAP_GFA_NRES = _process_final_density_map(self.temp_path, self.noDataValue
                                   , GFA_NRES_BUILD, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , np.ones_like(DENSITY_INDICATOR_MAP_OSM_BGF)
                                   , 0
                                   , 1 
                                   , "GFA_NRES_related")
            del GFA_NRES_BUILD
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_GFA_NRES
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "GFA_NRES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            
            
            print("Create VOL_NRES")
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_GFA_NRES
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "VOL_NRES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            SaveLayerDict = expLyr(SaveLayerDict)
            del Final_DENSITY_INDICATOR_MAP_GFA_NRES
            
            print("Create NON-RES Buildings Energy Density function")
            ####################
            # LOAD: ConstPeriodBasedEnergyIntensity
            ####################
            filename = ("%s/%s.tif" %(self.temp_path, "EnergyIntensity_CP_Surf_Vol_HDD_ratio"))
            ConstPeriodBasedEnergyIntensity, geotransform_obj = SF.rrl(filename, data_type)
            VA *= ConstPeriodBasedEnergyIntensity
            DENSITY_INDICATOR_MAP_OSM_BGF *= ConstPeriodBasedEnergyIntensity
            del ConstPeriodBasedEnergyIntensity
            
            fn = OSM_DataQuality_corr_high_RES_output_fn
            OSM_DataQuality_corr_high_RES, geotransform_obj = SF.rrl(fn, data_type=data_type)
            fn = self.Corine_share_path_POP_weight
            POPweight_corineLC, geotransform_obj = SF.rrl(fn, data_type=data_type)
            
            
            Final_DENSITY_INDICATOR_MAP_ENERGY_NRES = _process_final_density_map(self.temp_path, self.noDataValue
                                   , VA, self.geotransform_obj_high_res
                                   , ARR_NUTS_ID_NUMBER
                                   , DENSITY_INDICATOR_MAP_OSM_BGF
                                   , OSM_DataQuality_corr_high_RES
                                   , POPweight_corineLC 
                                   , "GFA_NRES_related")
            del POPweight_corineLC, OSM_DataQuality_corr_high_RES, DENSITY_INDICATOR_MAP_OSM_BGF, VA   
            
            filename = "DENSITY_MAP_ENERGY_NRES"
            density_map_energy_nres_fn = ("%s/%s.tif" %(self.temp_path, filename))
            SaveLayerDict["Final_DENSITY_INDICATOR_MAP_ENERGYNRES"] =   [density_map_energy_nres_fn
                                                  , self.geotransform_obj_high_res
                                                  , data_type
                                                  , Final_DENSITY_INDICATOR_MAP_ENERGY_NRES, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
            #Create NON-RES Buildings Energy Layer
            print("Create NON-RES Buildings Energy Layer")
            SaveLayerDict.update(DCSV2Map.dist_csv_data2map(self.proc_data_path, self.noDataValue
                                       , Final_DENSITY_INDICATOR_MAP_ENERGY_NRES
                                       , self.geotransform_obj_high_res
                                       , ARR_NUTS_ID_NUMBER
                                       , csv_input_data_file
                                       , "ENERGY_HEATING_NRES"
                                       , ADD_ID_MAP= ADD_ID_MAP))
            
            
            elapsed_time = time.time() - st1
            print("Process 5 took: %4.1f seconds" %elapsed_time)
            print("Process 5 took: %4.1f seconds" %elapsed_time)
            print("Export Results Maps")
            SaveLayerDict = expLyr(SaveLayerDict)
            del Final_DENSITY_INDICATOR_MAP_ENERGY_NRES
            del ARR_NUTS_ID_NUMBER, ARR_LAU2_ID_NUMBER
            ADD_ID_MAP = None

        
        elapsed_time = time.time() - start_time
        
        print("\n\n\n######\n\nThe whole process took: %4.1f seconds\n\n\n" %elapsed_time)

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        if del_temp_path:
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)
        print ("Done!")
        return

    def calc_EnergyIntensity_CP_Surf_Vol_HDD_ratio(self, results_file_name):
        """ Calc relative Energy Intensity per Floor Area
        """
        
        ConstPeriodBasedEnergyIntensity, geotransform_obj = CRL.clip_raster_layer(self.CPbasedEnergyIntensity_fn_path
                                                            , self.REFERENCE_geotransform_obj
                                                            , self.REFERENCE_RasterSize)   

        fname_ = ("%s/%s.tif" %(self.temp_path, "ConstPeriodBasedEnergyIntensity"))
        data_type = "f4"
        SaveLayerDict = {}
        SaveLayerDict["ConstPeriodBasedEnergyIntensity"] =   [fname_
                                              , geotransform_obj
                                              , data_type
                                              , ConstPeriodBasedEnergyIntensity, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        
        try:
            Surface_VolumeBasedEnergyIntensity, geotransform_obj = CRL.clip_raster_layer(self.Surface_Volumne_basedEnergyIntensity_fn_path
                                                        , self.REFERENCE_geotransform_obj
                                                        , self.REFERENCE_RasterSize)            
        except:
            Surface_VolumeBasedEnergyIntensity = np.ones_like(ConstPeriodBasedEnergyIntensity)
        Surface_VolumeBasedEnergyIntensity = SOHR.FillWithAverage(Surface_VolumeBasedEnergyIntensity)   
        
        
        fname_ = ("%s/%s.tif" %(self.temp_path, "Surface_VolumeBasedEnergyIntensity"))
        SaveLayerDict["Surface_VolumeBasedEnergyIntensity"] =   [fname_
                                              , geotransform_obj
                                              , data_type
                                              , Surface_VolumeBasedEnergyIntensity, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        ConstPeriodBasedEnergyIntensity *= (Surface_VolumeBasedEnergyIntensity ** 0.333)

        del Surface_VolumeBasedEnergyIntensity
        
        HDDBasedEnergyIntensity, geotransform_obj = CRL.clip_raster_layer(self.HDDbasedEnergyIntensity_fn_path
                                                        , self.REFERENCE_geotransform_obj
                                                        , self.REFERENCE_RasterSize)
        fname_ = ("%s/%s.tif" %(self.temp_path, "HDDBasedEnergyIntensity"))
        SaveLayerDict["HDDBasedEnergyIntensity"] =   [fname_
                                              , geotransform_obj
                                              , data_type
                                              , HDDBasedEnergyIntensity, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        
        ConstPeriodBasedEnergyIntensity *= HDDBasedEnergyIntensity
        del HDDBasedEnergyIntensity
        SaveLayerDict["EnergyIntensityIndicator"] =   [results_file_name
                                              , geotransform_obj
                                              , data_type
                                              , ConstPeriodBasedEnergyIntensity, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        
        del ConstPeriodBasedEnergyIntensity
        
        return
      
    def calc_OSM_LAYER(self
                        , OSMBGF_path
                        , OSMBFP_path
                        , OutPutRasterPath
                        , ResIncreaseFactor
                        , OSM_GFA_per_Inhab
                        , arr_soilseal_cut
                        , BGF_nRES_min
                        , arr_pop_cut
                        , ARR_NUTS_ID_NUMBER
                        , DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn
                        , OSM_DataQuality_corr_high_RES_output_fn):
        """
        
        """
        
        
        st1 = time.time()
        OSM_BGF_cut, geotransform_obj = CRL.clip_raster_layer(OSMBGF_path
                                                        , self.REFERENCE_geotransform_obj
                                                        , self.REFERENCE_RasterSize) 
        data_type  = "f4"
        # OpenStreetMap GrossFloorArea is at least 25 % of the share of JRC soilsealing (in percent) per pixel assuming average floor number of at least 
        # 1 floors multiplied  by the plot area of the pixel 
        # print(np.sum(OSM_BGF_cut))
        OSM_BGF_cut = np.maximum(OSM_BGF_cut, arr_soilseal_cut / 100 * 0.25 * 1.0 * geotransform_obj[1]**2) 
        # print(np.sum(OSM_BGF_cut2))
        # print(np.max(OSM_BGF_cut2 - OSM_BGF_cut))
        
        
        del arr_soilseal_cut
        SaveLayerDict = {}
        SaveLayerDict["OSM_BGF_cut"] =   ["%s_cut_corr_ESM.tif" %OutPutRasterPath[:-4], self.geotransform_obj_high_res
                                              , data_type
                                              , OSM_BGF_cut, self.noDataValue]

        #ResIncreaseFactor = PopulationRasterResolution / TARGET_RESOLUTION
        
        OSM_BGF_low_RES =  SOHR.CalcLowResSum(OSM_BGF_cut, ResIncreaseFactor) 
        BGF_nRES_min_low_RES =  SOHR.CalcLowResSum(BGF_nRES_min, ResIncreaseFactor)
        del BGF_nRES_min

        GFA_per_Inhab = (np.maximum(OSM_BGF_low_RES * 0.4 , OSM_BGF_low_RES - BGF_nRES_min_low_RES)) / np.maximum(1, arr_pop_cut)
        
        del BGF_nRES_min_low_RES
        SaveLayerDict["GFA_per_Inhab"] =   [OSM_GFA_per_Inhab, self.REFERENCE_geotransform_obj
                                              , data_type
                                              , GFA_per_Inhab , self.noDataValue]
        del arr_pop_cut
        
        
        
        ##Transfer to high Resolution again 
        #data_SS_CLC = SOHR.CalcHighRes(data_SS_CLC_1_km, 0) + 10 ** - 4
        
        if EXPORT_AT_THE_END == False:
            SaveLayerDict = expLyr(SaveLayerDict)
                
            elapsed_time = time.time() - st1
            print("Process OSM took: %4.1f seconds" %elapsed_time)
        
        #Read NUTS Data
        (NUTS3_DATA, EXPORT_COLUMNS
         , SCALING_FACTOR, CUTOFF_Value) = RCD.READ_CSV_DATA(self.csv_input_data_NUTS3_path)
        ONES = np.ones_like(ARR_NUTS_ID_NUMBER)
        
        NUTS_Data_POP  = np.maximum(4, NUTS3_DATA.view(np.recarray)["POP_2012"])
        RESULTS_POP = CDM.CreateFinalMap(ONES, ARR_NUTS_ID_NUMBER, NUTS_Data_POP)
        RESULTS_POP_LOW_RES =  SOHR.CalcLowResSum(RESULTS_POP, ResIncreaseFactor) / ResIncreaseFactor ** 2 
        if DEBUG == True:
            SaveLayerDict["RESULTS_POP_LOW"] =   ["%s/_RESULTS_POP_LOW_RES.tif" %(self.temp_path), self.REFERENCE_geotransform_obj
                                                  , data_type
                                                  , RESULTS_POP_LOW_RES , self.noDataValue]
            SaveLayerDict["RESULTS_POP"] =   ["%s/_RESULTS_POP.tif" %(self.temp_path), self.geotransform_obj_high_res
                                                  , data_type
                                                  , RESULTS_POP, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
        del RESULTS_POP
        
        NUTS_Data_NFA  = np.maximum(4, NUTS3_DATA.view(np.recarray)["GFA_RES_BUILD"]) #  data are actually net floor areas
        # Correction from Netfloor Area to Gross floor Area
        RESULTS_GFA = 1.2 * CDM.CreateFinalMap(ONES, ARR_NUTS_ID_NUMBER, NUTS_Data_NFA)
        RESULTS_GFA_LOW_RES =  SOHR.CalcLowResSum(RESULTS_GFA, ResIncreaseFactor) / ResIncreaseFactor ** 2
        if DEBUG == True:
            SaveLayerDict["RESULT_GFA_LOW"] =   ["%s/_RESULT_GFA_LOW.tif" %(self.temp_path), self.REFERENCE_geotransform_obj
                                                  , data_type
                                                  , RESULTS_GFA_LOW_RES, self.noDataValue]
            SaveLayerDict["RESULT_GFA"] =   ["%s/_RESULT_GFA.tif" %(self.temp_path), self.geotransform_obj_high_res
                                                  , data_type
                                                  , RESULTS_GFA, self.noDataValue]
        del RESULTS_GFA   
        NUTS_Data_DW  = np.maximum(1, NUTS3_DATA.view(np.recarray)["POP_NumDW"])
        RESULT_DW = CDM.CreateFinalMap(ONES, ARR_NUTS_ID_NUMBER, NUTS_Data_DW)
        RESULTS_DW_LOW_RES =  SOHR.CalcLowResSum(RESULT_DW, ResIncreaseFactor) / ResIncreaseFactor ** 2
        
        del ONES
        if DEBUG == True:
            SaveLayerDict["RESULT_DW_LOW"] =   ["%s/_RESULT_DW_LOW.tif" %(self.temp_path), self.REFERENCE_geotransform_obj
                                                  , data_type
                                                  , RESULTS_DW_LOW_RES, self.noDataValue]
            SaveLayerDict["RESULT_DW"] =   ["%s/_RESULT_DW.tif" %(self.temp_path), self.geotransform_obj_high_res
                                                  , data_type
                                                  , RESULT_DW, self.noDataValue]

            SaveLayerDict = expLyr(SaveLayerDict)
        del RESULT_DW
            
        # RESULTS_POP_LOW_RES: tds Person,  RESULTS_DW_LOW_RES: Dwellings
        # RESULTS_GFA_LOW_RES: Mio. m²
        # min_GFA: Min Gross Floor Area per Person
        
        min_GFA = (1000 * RESULTS_GFA_LOW_RES) / (0.1 + RESULTS_POP_LOW_RES)
        idxM = min_GFA < 5
        min_GFA[idxM] =  (55 * (RESULTS_DW_LOW_RES / 1000) / (0.1 + RESULTS_POP_LOW_RES))[idxM]
        idxM = min_GFA < 5
        min_GFA[idxM] = 30 # Gross floor area per capita
        idxM = RESULTS_POP_LOW_RES < 5
        min_GFA[idxM] = 0
        
        SaveLayerDict["min_GFA"] =   ["%s/_RESULT_min_GFA.tif" %(self.temp_path), self.geotransform_obj_high_res
                                                  , data_type
                                                  , min_GFA, self.noDataValue]
        del RESULTS_DW_LOW_RES, RESULTS_GFA_LOW_RES, RESULTS_POP_LOW_RES
        print(" Calculation of min_GFA per Raster done!")
        OSM_DataQuality_Indicator = np.ones_like(OSM_BGF_low_RES)
        del OSM_BGF_low_RES

        

        idxM_15 = (GFA_per_Inhab < 15)
        
        OSM_Corr_factor = np.maximum(1, 
                                np.minimum(4, min_GFA / (0.1 + GFA_per_Inhab)))
        
        if DEBUG == True:
            SaveLayerDict["OSM_correction_factor"] =   ["%s/_RESULT_OSM_Corr_Faktor.tif" %(self.temp_path)
                                                        , self.REFERENCE_geotransform_obj
                                              , data_type
                                              , OSM_Corr_factor, self.noDataValue]
            SaveLayerDict = expLyr(SaveLayerDict)
        
        OSM_DataQuality_Indicator[idxM_15] = GFA_per_Inhab[idxM_15] / 20
        OSM_Corr_factor_high_RES =  SOHR.CalcHighRes(OSM_Corr_factor, ResIncreaseFactor)
        
        DENSITY_INDICATOR_MAP_OSM_BGF =  OSM_Corr_factor_high_RES  * OSM_BGF_cut 
        SaveLayerDict["DENSITY_INDICATOR_MAP_OSM_BGF"] =   [DENSITY_INDICATOR_MAP_OSM_BGF_ouput_fn
                                              , self.REFERENCE_geotransform_obj
                                              , data_type
                                              , DENSITY_INDICATOR_MAP_OSM_BGF, self.noDataValue]
        
        print(" Calculation of OSM correction factor done!")
        del OSM_Corr_factor_high_RES, OSM_Corr_factor, OSM_BGF_cut
        OSM_DataQuality_corr_high_RES  = SOHR.CalcHighRes(OSM_DataQuality_Indicator, ResIncreaseFactor) 
        SaveLayerDict["OSM_DataQuality_corr_high_RES"] =   [OSM_DataQuality_corr_high_RES_output_fn
                                              , self.geotransform_obj_high_res
                                              , data_type
                                              , OSM_DataQuality_corr_high_RES, self.noDataValue]
        print(" Calculation of corrected OSM GFA done!")
        
        OSM_BFP_cut, geotransform_obj = CRL.clip_raster_layer(OSMBFP_path
                                                        , self.REFERENCE_geotransform_obj
                                                        , self.REFERENCE_RasterSize)
        fn_ = "%s/%s" %(self.temp_path, "_____0__FINAL_OSMbuildings_FOOTPRINT.tif")
        SaveLayerDict["OSM_floors_Model"] =   [fn_
                                               , self.geotransform_obj_high_res
                                              , data_type
                                              , OSM_BFP_cut, self.noDataValue]
        
        OSM_floors_Model = DENSITY_INDICATOR_MAP_OSM_BGF / np.maximum(1, OSM_BFP_cut)
        SaveLayerDict = expLyr(SaveLayerDict)
        
        del OSM_BFP_cut
        print(" Calculation of corrected OSM_floors_Model done!")
        SaveLayerDict["OSM_floors_Model"] =   ["%s/_RESULT_OSM_floors_Model.tif" %(self.temp_path)
                                               , self.geotransform_obj_high_res
                                              , data_type
                                              , OSM_floors_Model, self.noDataValue]
        SaveLayerDict = expLyr(SaveLayerDict)
        
        del OSM_floors_Model, GFA_per_Inhab
        return (DENSITY_INDICATOR_MAP_OSM_BGF
                , OSM_DataQuality_corr_high_RES)
        
          
                
         
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
    
    def create_sum_of_res_nres(self, copy2GITDIR):
        
        """Creates Layer with sum of RES and Non-Res 
            and copies (optional) data to the local GITLAB directory
        """
        if copy2GITDIR == True:
            dir_git = (os.path.abspath("/".join((self.proc_data_path.replace("\\","/").split("/"))[:-4]) + "/GITLAB") + "/")
            print(dir_git)
            assert dir_git
            
        
        fn_dict = {}
        fn_dict["GFA_TOT_BUILD"] = ["GFA_TOT_BUILD"
                                    , "GFA_RES_BUILD", "GFA_NRES_BUILD"
                                    , "gfa_tot_curr_density"
                                    , "gfa_res_curr_density"
                                    , "gfa_nonres_curr_density"]
        
        fn_dict["VOL_TOT_BUILD"] = ["VOL_TOT_BUILD"
                                    , "VOL_RES_BUILD", "VOL_NRES_BUILD"
                                    , "vol_tot_curr_density"
                                    , "vol_res_curr_density"
                                    , "vol_nonres_curr_density"]
        fn_dict["ENERGY_HEATING_TOT_2012"] = ["ENERGY_HEATING_TOT_2012"
                                              , "ENERGY_HEATING_RES_2012"
                                              , "ENERGY_HEATING_NRES_2012"
                                    , "heat_tot_curr_density"
                                    , "heat_res_curr_density"
                                    , "heat_nonres_curr_density"]
        
        data_type = "f4"
        SaveLayerDict = {}
        for key_ in fn_dict:
            
            fn_res = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][0])
            fn1 = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][1])
            fn2 = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][2])
            
            for REG in ["LAU2", "NUTS"]:
                fn_csv1 = fn1[:-4]+"_%s_ID_NUMBER.csv" % REG
                fn_csv2 = fn2[:-4]+"_%s_ID_NUMBER.csv" % REG
                fn_csvres = fn_res[:-4]+"_%s_ID_NUMBER.csv" % REG
            
                data_csv1 = np.genfromtxt(fn_csv1, "f4", delimiter=",")
                while data_csv1[1, 0] !=1.0:
                    data_csv1 = data_csv1[1:, :]
                data_csv2 = np.genfromtxt(fn_csv2, "f4", delimiter=",")
                while data_csv2[1, 0] !=1.0:
                    data_csv2 = data_csv2[1:, :]
                data_total = np.zeros_like(data_csv1)   
                data_total[:,:] = data_csv1
                data_total[:, 1] += data_csv2[:, 1]
            
                np.savetxt(fn_csv1, data_csv1, delimiter=",", header="%s_number,value" % REG, comments="")
                np.savetxt(fn_csv2, data_csv2, delimiter=",", header="%s_number,value" % REG, comments="")
                np.savetxt(fn_csvres, data_total, delimiter=",", header="%s_number,value" % REG, comments="")
                
            arr1, geotransform_obj = SF.rrl(fn1, data_type=data_type)
            arr2, geotransform_obj = SF.rrl(fn2, data_type=data_type)
            
            arr_res = np.zeros_like(arr1)
            arr_res += arr1
            arr_res += arr2
            SaveLayerDict["XXX"] =   [fn_res
                                        , geotransform_obj
                                        , data_type
                                        , arr_res, self.noDataValue]
        
            if os.path.exists(fn_res):
                os.remove(fn_res)
            SaveLayerDict = expLyr(SaveLayerDict)
            
            if copy2GITDIR == True:
                
                assert os.path.exists(dir_git) 
                for i in range(3):
                    for fn_ending in ["tif", "tfw"]:
                        fn = "%s/RESULTS_%s.%s" % (self.proc_data_path, fn_dict[key_][i], fn_ending)
                        fn_res = "%s/%s/data/%s.%s" % (dir_git, fn_dict[key_][i+3]
                                                      , fn_dict[key_][i+3], fn_ending)
                        if os.path.exists(fn_res):
                            os.remove(fn_res)
                        shutil.copy2(fn, fn_res)
                    for REG in ["LAU2", "NUTS"]:
                        fn = "%s/RESULTS_%s_%s_ID_NUMBER.csv" % (self.proc_data_path, fn_dict[key_][i], REG)
                        fn_res = "%s/%s/data/%s_%s_ID_NUMBER.csv" % (dir_git, fn_dict[key_][i+3]
                                                      , fn_dict[key_][i+3], REG)
                        if os.path.exists(fn_res):
                            os.remove(fn_res)
                        shutil.copy2(fn, fn_res)
                       
        if copy2GITDIR == True:
            fn_dict = {}               
            fn_dict["POP_2012"] = ["POP_2012"
                                    , "pop_tot_curr_density"]

            for key_ in fn_dict:
                fn1 = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][0])
                for REG in ["LAU2", "NUTS"]:
                    fn_csv1 = fn1[:-4]+"_%s_ID_NUMBER.csv" % REG
                    data_csv1 = np.genfromtxt(fn_csv1, "f4", delimiter=",")
                    while data_csv1[1, 0] !=1.0:
                        data_csv1 = data_csv1[1:, :]
                    
                    np.savetxt(fn_csv1, data_csv1, delimiter=",", header="%s_number,value" % REG, comments="")
                
                for fn_ending in ["tif", "tfw"]:
                    fn = "%s/RESULTS_%s.%s" % (self.proc_data_path, fn_dict[key_][0], fn_ending)
                    fn_res = "%s/%s/data/%s.%s" % (dir_git, fn_dict[key_][1]
                                                  , fn_dict[key_][1], fn_ending)
                    shutil.copy2(fn, fn_res)
                
                for REG in ["LAU2", "NUTS"]:
                        fn = "%s/RESULTS_%s_%s_ID_NUMBER.csv" % (self.proc_data_path, fn_dict[key_][0], REG)
                        fn_res = "%s/%s/data/%s_%s_ID_NUMBER.csv" % (dir_git, fn_dict[key_][1]
                                                      , fn_dict[key_][1], REG)
                        if os.path.exists(fn_res):
                            os.remove(fn_res)
                        shutil.copy2(fn, fn_res)
                    
        
        
            with open("%s/version_info.txt" % dir_git) as f:
                content = f.readlines()
                # you may also want to remove whitespace characters like `\n` at the end of each line
                content = [x.strip() for x in content] 
            f.close()
            try:
                version = content[0].split(".")            
            except:
                version = ["0","0","99"]        
            try:
                
                eval(version[1])
            except:
                version = ["0","0","99"]  
                  
            version_new = "%s.%s.0" %(version[0], eval(version[1])+1)
            created_new = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            
            with open("%s/version_info.txt" % dir_git, "w") as f:
                f.write(version_new + "\n")
                f.write(created_new + "\n")
                f.write("PREV_VERSION: %s " % content[0] + "\n")
                f.write("PREV_CREATION TIME: %s " % content[1] + "\n")
                f.write("Full Backlog:\n")
                f.write("     " + content[2].strip()+ "\n")
                f.write("     " + content[3].strip()+ "\n")
                for l in content[5:]:
                    f.write("     " + l.strip()+ "\n")
        
        print ("Done!")

        
    def create_floor_area_per_construction_period(self, NUTS3_feat_id_LIST, copy2GITDIR):
        
        """Creates Layer with sum of RES and Non-Res 
            and copies (optional) data to the local GITLAB directory
        """
        
        if copy2GITDIR == True:
            dir_git = (os.path.abspath("/".join((self.proc_data_path.replace("\\","/").split("/"))[:-3]) + "/GITLAB") + "/")
            assert os.path.exists(os.path.abspath("/".join((self.proc_data_path.replace("\\","/").split("/"))[:-3]) + "/GITLAB/"))
            print(dir_git)
        
        
        
        input_path_cp = "%s/SoilSeal_ConstrPeriods" % self.preproccessed_input_data
        
    
        fn_share_cp_1975 = "%s/GHS_BUILT_%i_100_share.tif" %(input_path_cp, 1975)
        fn_share_cp_1990 = "%s/GHS_BUILT_%i_100_share.tif" %(input_path_cp, 1990)
        fn_share_cp_2000 = "%s/GHS_BUILT_%i_100_share.tif" %(input_path_cp, 2000)
        fn_share_cp_2014 = "%s/GHS_BUILT_%i_100_share.tif" %(input_path_cp, 2014)
        
        
        
        fn_gfa_res = "%s/RESULTS_GFA_RES_BUILD.tif" % self.proc_data_path
        fn_gfa_nres="%s/RESULTS_GFA_NRES_BUILD.tif" % self.proc_data_path
        
        
        fn_dict = {}
        fn_dict["GFA_TOT_BUILD"] = ["GFA_TOT_BUILD"
                                    , "GFA_RES_BUILD", "GFA_NRES_BUILD"
                                    , "gfa_tot_curr_density"
                                    , "gfa_res_curr_density"
                                    , "gfa_nonres_curr_density"]
    
        
        
        (REFERENCE_RasterResolution, HighRes_gt_obj, self.LOAD_DATA_PREVIOUS) = \
                self.load_reference_raster_lyr(self.NUTS3_vector_path,
                                               self.strd_raster_path_full, 
                                               self.temp_path, NUTS3_feat_id_LIST
                                               , deletedata=False)
        
        geotransform_obj = self.REFERENCE_geotransform_obj
        REFERENCE_RasterSize = self.REFERENCE_RasterSize
        
        data_type = "f4"
        SaveLayerDict = {}
        
        arr_gfa_res, geotransform_obj = CRL.clip_raster_layer(fn_gfa_res
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
        
        #arr_gfa_res, geotransform_obj = SF.rrl(fn_gfa_res, data_type=data_type)
        
        REFERENCE_RasterSize = arr_gfa_res.shape
        
        
        ARR_NUTS_ID_NUMBER, geotransform_obj = CRL.clip_raster_layer(self.NUTS_id_number
                                                , geotransform_obj
                                                , REFERENCE_RasterSize)  
        ARR_LAU2_ID_NUMBER, geotransform_obj = CRL.clip_raster_layer(self.LAU2_id_number
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
        

        TABLE_RESULTS_LAU = np.zeros((np.max(ARR_LAU2_ID_NUMBER)+1, 10), dtype="f4")
        TABLE_RESULTS_NUTS = np.zeros((np.max(ARR_NUTS_ID_NUMBER)+1, 10), dtype="f4")
        
        for j in range(2):
            if j == 0:
                NRES = ""
                gfa_arr = arr_gfa_res
            else:
                NRES = "N"
                del arr_gfa_res
                gfa_arr, geotransform_obj = CRL.clip_raster_layer(fn_gfa_nres
                                                , HighRes_gt_obj
                                                , REFERENCE_RasterSize)
            for i in range(4):
                if i == 0:
                    if j == 0:
                        cp_1975, geotransform_obj = CRL.clip_raster_layer(fn_share_cp_1975
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
                    CPshare = cp_1975
                    f = "-1975"
                    
                elif i == 1:
                    if j == 0:
                        cp_1990, geotransform_obj = CRL.clip_raster_layer(fn_share_cp_1990
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
                    CPshare = cp_1990
                    f = "75-90"
                elif i == 2:
                    if j == 0:
                        cp_2000, geotransform_obj = CRL.clip_raster_layer(fn_share_cp_2000
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
                    CPshare = cp_2000
                    f = "90-00"
                else:
                    if j == 0:
                        cp_2014, geotransform_obj = CRL.clip_raster_layer(fn_share_cp_2014
                                                , geotransform_obj
                                                , REFERENCE_RasterSize) 
                    CPshare = cp_2014
                    f = "00-14"
                    
                res = gfa_arr * CPshare
                
                tab = CDM.CreateResultsTableperIndicator(res, ARR_LAU2_ID_NUMBER)  
                TABLE_RESULTS_LAU[:, 0] = tab[:, 0]
                TABLE_RESULTS_LAU[:, i+1 + j*4] = tab[:, 1]
                
                tab = CDM.CreateResultsTableperIndicator(res, ARR_NUTS_ID_NUMBER)   
                TABLE_RESULTS_NUTS[:, 0] = tab[:, 0]
                TABLE_RESULTS_NUTS[:, i+1 + j*4] = tab[:, 1]
                
                
                fn_res = "%s/RESULTS_%s.tif" % (self.proc_data_path, "GFA_%sRES_CP_%s" % (NRES,f))
            
                SaveLayerDict["XXX"] =   [fn_res
                                                  , geotransform_obj
                                                  , data_type
                                                  , res, self.noDataValue]
                SaveLayerDict = expLyr(SaveLayerDict)
        
            
        header ="ID,GFA_RES_before78,GFA_RES_79-90,GFA_RES_91-00,GFA_RES_00-14"        
        header +="GFA_NRES_before78,GFA_NRES_79-90,GFA_NRES_91-00,GFA_NRES_00-14"
        fn_ = ("%s/%s.csv" %(self.temp_path, "GFA_per_CP_and_LAU"))
        np.savetxt(fn_, np.round(TABLE_RESULTS_LAU, 1), delimiter=","
                   , header=header, comments="")
        
        fn_ = ("%s/%s.csv" %(self.temp_path, "GFA_per_CP_and_NUTS"))
        np.savetxt(fn_, np.round(TABLE_RESULTS_NUTS, 1), delimiter=","
                   , header=header, comments="")
            
        print("Done")
        return
        """
        for key_ in fn_dict:
            
            fn_res = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][0])
            fn1 = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][1])
            fn2 = "%s/RESULTS_%s.tif" % (self.proc_data_path, fn_dict[key_][2])
            
            arr1, geotransform_obj = SF.rrl(fn1, data_type=data_type)
            arr2, geotransform_obj = SF.rrl(fn2, data_type=data_type)
            
            arr_res = np.zeros_like(arr1)
            arr_res += arr1
            arr_res += arr2
            SaveLayerDict["XXX"] =   [fn_res
                                        , geotransform_obj
                                        , data_type
                                        , arr_res, self.noDataValue]
        
            if os.path.exists(fn_res):
                os.remove(fn_res)
            SaveLayerDict = expLyr(SaveLayerDict)
            
            if copy2GITDIR == True:
                
                assert os.path.exists(dir_git) 
                for i in range(3):
                    for fn_ending in ["tif", "tfw"]:
                        fn = "%s/RESULTS_%s.%s" % (self.proc_data_path, fn_dict[key_][i], fn_ending)
                        fn_res = "%s/%s/data/%s.%s" % (dir_git, fn_dict[key_][i+3]
                                                      , fn_dict[key_][i+3], fn_ending)
                        if os.path.exists(fn_res):
                            os.remove(fn_res)
                        shutil.copy2(fn, fn_res)
                       
        if copy2GITDIR == True:
            fn_dict = {}               
            fn_dict["POP_2012"] = ["POP_2012"
                                    , "pop_tot_curr_density"]
            
            for key_ in fn_dict:
                for fn_ending in ["tif", "tfw"]:
                    fn = "%s/RESULTS_%s.%s" % (self.proc_data_path, fn_dict[key_][0], fn_ending)
                    fn_res = "%s/%s/data/%s.%s" % (dir_git, fn_dict[key_][1]
                                                  , fn_dict[key_][1], fn_ending)
                    shutil.copy2(fn, fn_res)
                    
        
        
            with open("%s/version_info.txt" % dir_git) as f:
                content = f.readlines()
                # you may also want to remove whitespace characters like `\n` at the end of each line
                content = [x.strip() for x in content] 
            f.close()
            try:
                version = content[0].split(".")            
            except:
                version = ["0","0","99"]        
            try:
                
                eval(version[1])
            except:
                version = ["0","0","99"]  
                  
            version_new = "%s.%s.0" %(version[0], eval(version[1])+1)
            created_new = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            
            with open("%s/version_info.txt" % dir_git, "w") as f:
                f.write(version_new + "\n")
                f.write(created_new + "\n")
                f.write("PREV_VERSION: %s " % content[0] + "\n")
                f.write("PREV_CREATION TIME: %s " % content[1] + "\n")
                f.write("Full Backlog:\n")
                f.write("     " + content[2].strip()+ "\n")
                f.write("     " + content[3].strip()+ "\n")
                for l in content[5:]:
                    f.write("     " + l.strip()+ "\n") 
        """