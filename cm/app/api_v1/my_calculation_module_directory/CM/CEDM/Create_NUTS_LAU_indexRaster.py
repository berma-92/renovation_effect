import numpy as np
import shutil
import time #, gdal, ogr

import os
import sys




path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

import CM_intern.CEDM.modules.Subfunctions as SF
import CM_intern.common_modules.cliprasterlayer as CRL

from CM_intern.common_modules.exportLayerDict import export_layer as expLyr
from CM_intern.CEDM.modules.createIndexRasterMap import createIndexMap 


from CM_intern.common_modules.countries import COUNTRIES
import CM_intern.common_modules.readCsvData as RCD
import CM_intern.common_modules.array2raster as a2r

import pickle

COMPRESSION_LEVEL_FINAL_RESULTS = 9

DEBUG = True
#DEBUG = False
#PRINT_TEST_RESULTS = False
#linux = "linux" in sys.platform



LOWEST_RESOLUTION = 1000 #Meter
# define raster size
TARGET_RESOLUTION = 100 #Meter


fp = open('memory_profiler.log', 'w+') 
#sys.stdout = open("print_output.txt", "w")





class ClassCalcNUTSLAU_raster():
    
    def __init__(self, prj_path, prj_path_input
                 , prj_path_output, preproccessed_input_path):
        
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
        self.prj_path_preproccessed_input = "%s/%s" %(prj_path, preproccessed_input_path) 
        
        
        # Path containing processed Data
        self.proc_data_path    = self.prj_path_output  + os.sep + "Processed Data"    
        # Path containing temporal Data
        self.temp_path        = self.prj_path_output  + os.sep + "Temp"
        
        #create if doesn't exist
        if not os.path.exists(self.proc_data_path):
            os.makedirs(self.proc_data_path)
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        if not os.path.exists(self.prj_path_preproccessed_input):
            os.makedirs(self.prj_path_preproccessed_input)
        #self.pixelWidth = 100
        #self.pixelHeight = -100 
        
        # input data files
        # Standard Vector layer (Nuts 3 and LAU shape file)
        self.NUTS3_vector_path = self.org_data_path + "/vector_input_data/NUTS3.shp"
        self.LAU2_vector_path = self.org_data_path + "/vector_input_data/Communal2.shp"
        self.NUTS_id_number =  self.proc_data_path + "/NUTS3_id_number.tif"
        self.LAU2_id_number =  self.proc_data_path + "/LAU2_id_number.tif"
        self.Country_id_number = self.prj_path_preproccessed_input + "/COUNTRY_id_number.tif"
        
        self.NUTS_id_number_prepro =  self.prj_path_preproccessed_input + "/NUTS3_id_number.tif"
        self.LAU2_id_number_prepro =  self.prj_path_preproccessed_input + "/LAU2_id_number.tif"
        
        # Standard raster Layer
        self.strd_raster_path_full = "%s/%s" %(self.org_data_path, "Population.tif")
        

        # Clipped Raster layer
        
        self.NUTS3_cut_vector_path =  self.temp_path + "/NUTS3_cut.shp"
        self.LAU2_cut_vector_path =  self.temp_path + "/LAU2_cut.shp"
        self.NUTS_cut_id_number =  self.temp_path + "/NUTS3_cut_id_number.tif"
        self.LAU2_cut_id_number =  self.temp_path + "/LAU2_cut_id_number.tif"
        
        #outputs
        self.MOST_RECENT_CUT = "%s/MOST_RECENT_CUT.pk" %self.prj_path_output 

        
        self.csvNutsData = "%s/%s" %(self.org_data_path, "NUTS3_data.csv")
        
      
        # array2raster output datatype
        self.datatype_int = 'uint32'
        #self.datatype_int16 = 'uint16'
        self.datatype = "float32"
        # common parameters
        self.noDataValue = 0
          
    #@profile(stream=fp)     
    def main_process(self, NUTS3_feat_id_LIST):
        
        
        
        
        start_time = time.time()
        
        
        
        SaveLayerDict = {}
        # Load Raster Reference Layer
        (REFERENCE_RasterResolution, HighRes_gt_obj, self.LOAD_DATA_PREVIOUS
         , Ref_layer_is_uncut) = \
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
                
                #ARR_LAU2_ID_NUMBER, geotransform_obj = SF.rrl(OutPutRasterPathLau2, data_type=dataType32)
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
            

      
        
            SaveLayerDict = expLyr(SaveLayerDict)
            if Ref_layer_is_uncut == True or 1==1:
                shutil.copy2(OutPutRasterPathNuts, self.NUTS_id_number)
                shutil.copy2(OutPutRasterPathLau2, self.LAU2_id_number)
                
                shutil.copy2(OutPutRasterPathNuts, self.NUTS_id_number_prepro)
                shutil.copy2(OutPutRasterPathLau2, self.LAU2_id_number_prepro)

                
            elapsed_time = time.time() - st
            print("Process Create INDEX MAPS took: %4.1f seconds" %elapsed_time)
        

        print("create Country ID Map")
        elapsed_time = time.time() - start_time
        start_time2 = time.time()
        NutsData = RCD.READ_CSV_DATA(self.csvNutsData , delimiter=",", skip_header=6)[0]
        if NutsData["COUNTRY_ID"][5] == 0:
            CNAME = np.unique(NutsData["COUNTRY_CODE"])
            cid = 0
            for ele in COUNTRIES:
                for ele2 in CNAME:
                    if ele[1] == ele2:
                        idx = NutsData["COUNTRY_CODE"] == ele2
                        NutsData["COUNTRY_NRCODE"][idx] = ele[0]
                        cid += 1
                        NutsData["COUNTRY_ID"][idx] = cid
            #np.savetxt(self.csvNutsData + "_new_cnr", NutsData['COUNTRY_NRCODE'], delimiter=",")
            #np.savetxt(self.csvNutsData + "_new_id", NutsData['COUNTRY_ID'], delimiter=",")
        ARR_COUNTRY_ID_NUMBER = np.zeros_like(ARR_NUTS_ID_NUMBER)
        
        for jj, CID in enumerate(np.unique(NutsData["COUNTRY_ID"])):
            print(jj)
            #if jj > 5:
            #    break
            NUTS3IDlist = NutsData["DI"][NutsData["COUNTRY_ID"] == CID]
            NUTS3_list = np.zeros(NUTS3IDlist.shape[0], dtype="uint16")
            for kk, ele in enumerate(NUTS3IDlist):
                id_ = ele[3:]
                if id_.isnumeric():
                    id_ = int(id_)
                    NUTS3_list[kk] = id_
                else:
                    print("Cannot convert to integer %s"%id_)
            if NUTS3_list[-1] - NUTS3_list[0] + 1 == NUTS3IDlist.shape[0]:
                idx = np.logical_and(ARR_NUTS_ID_NUMBER >= NUTS3_list[0]
                                     , ARR_NUTS_ID_NUMBER <= NUTS3_list[-1])
                ARR_COUNTRY_ID_NUMBER[idx] = CID
            else:
                print("CHECXK COUNTRY: %i" % CID)
        SaveLayerDict["COUNTRY_ID_NUMBER"] =   [self.Country_id_number , geotransform_obj
                                                      , "int8"
                                                      , ARR_COUNTRY_ID_NUMBER , self.noDataValue]
          
            
        SaveLayerDict = expLyr(SaveLayerDict)
        elapsed_time2 = time.time() - start_time2
        print("\n\n\n######\n\nThe whole process took: %4.1f + %4.1f seconds\n\n\n" %(elapsed_time, elapsed_time2))

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        
        print ("Done!")
        return

    
    
        
        
    def load_reference_raster_lyr(self, NUTS3_vector_path, strd_raster_path_full, outputpath, NUTS3_feat_id_LIST, deletedata=True):
        
        #SaveLayerDict = {}
        # Get current extent -> Use the Population 1x1km raster as reference Layer
        key_field = "NUTS_ID" 
        REFERENCE_RASTER_LAYER_COORD, Layer_is_uncut = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(strd_raster_path_full
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
        
        return (REFERENCE_RasterResolution, HighRes_gt_obj, LOAD_DATA_PREVIOUS, Layer_is_uncut)
    
    