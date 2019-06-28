
import numpy as np
import os
import time
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
    
import CM_intern.CEDM.modules.cyf.create_density_map as CDM
import CM_intern.CEDM.modules.Subfunctions as SF
from  CM_intern.common_modules.exportLayerDict import export_layer as expLyr
import CM_intern.common_modules.cliprasterlayer as CRL

import pickle

TARGET_RESOLUTION = 100

def load_reference_raster_lyr(NUTS3_vector_path, strd_raster_path_full, outputpath, NUTS3_feat_id_LIST
                              , MOST_RECENT_CUT=""):
    
    datatype_int = 'uint32'
    #self.datatype_int16 = 'uint16'
    datatype = "float32"
    # common parameters
    noDataValue = 0
         
    #SaveLayerDict = {}
    # Get current extent -> Use the Population 1x1km raster as reference Layer
    key_field = "NUTS_ID" 
    REFERENCE_RASTER_LAYER_COORD, Layer_is_uncut = CRL.create_reference_raster_layer_origin_extent_of_vctr_feat(strd_raster_path_full
                , NUTS3_vector_path, NUTS3_feat_id_LIST
                , Vctr_key_field=key_field)
    (REFERENCE_geotransform_obj, REFERENCE_RasterSize
     , REFERENCE_RESOLUTION, REFERENCE_extent) = REFERENCE_RASTER_LAYER_COORD
    
    REFERENCE_RasterResolution = REFERENCE_geotransform_obj[1]
    
    gto_hr = list(REFERENCE_geotransform_obj)
    gto_hr[1] = TARGET_RESOLUTION
    gto_hr[5] = -TARGET_RESOLUTION
    HighRes_gt_obj = tuple(gto_hr)
    
    SaveLayerDict = {}
    SaveLayerDict["Reference"] =   ["%s/REFERENCE.tif" % outputpath, REFERENCE_geotransform_obj
                                                  , datatype_int
                                                  , np.ones((REFERENCE_RasterSize), dtype=datatype_int) , noDataValue]
    
    
    # If data are the same as previous cut, then loading data can be done
    LOAD_DATA_PREVIOUS = False
    filename = MOST_RECENT_CUT
    if os.path.exists(MOST_RECENT_CUT):
        try:
            with open(MOST_RECENT_CUT, 'rb') as fobject:
                PREV_CUT = pickle.load(fobject)
                fobject.close()
            if PREV_CUT == REFERENCE_RASTER_LAYER_COORD:
                LOAD_DATA_PREVIOUS = True
        except Exception as e:
            print("Cannot import %s"%MOST_RECENT_CUT)
            print(e)
    
    
    if LOAD_DATA_PREVIOUS != True:

        with open(filename, 'wb') as fobject:
            pickle.dump(REFERENCE_RASTER_LAYER_COORD, fobject, protocol=2)
            fobject.close()
    SaveLayerDict = expLyr(SaveLayerDict)
    
    return (REFERENCE_RasterResolution, HighRes_gt_obj, LOAD_DATA_PREVIOUS, Layer_is_uncut, REFERENCE_geotransform_obj, REFERENCE_RasterSize)



def main(main_path, path_in_raw, preproccessed_input_path, prj_path_output):  
    st = time.time()
    
    data_type = "uint8"
    
    MOST_RECENT_CUT = main_path + prj_path_output + "/MOST_RECENT_CUT.pk" 
    prepro_path = main_path + preproccessed_input_path
    org_data_path = main_path + path_in_raw
    p_ = org_data_path
    pi_ = org_data_path + "/vector_input_data/"
    NUTS3_vector_path = pi_ + "/NUTS3.shp"
    strd_raster_path_full = "%s/%s" %(org_data_path, "Population.tif")
    temp_path = "/home/simulant/workspace/project/Hotmaps_DATA/heat_density_map/output_2/"  + os.sep + "Temp"
    SoilSeal_path_full = "%s/%s" %(org_data_path, "_____ESM100m_final.tif")
    
    
    
    #p_ = "/home/simulant/workspace/project/Hotmaps_DATA/heat_density_map/output/"
    
    
    
    sd = ""
    print(os.path.exists(p_))
    print(os.path.exists(pi_))
    fn = []
    NUTS3_feat_id_LIST = range(12000)
    (REFERENCE_RasterResolution, HighRes_gt_obj, LOAD_DATA_PREVIOUS
             , Ref_layer_is_uncut, REFERENCE_geotransform_obj, REFERENCE_RasterSize) = \
                    load_reference_raster_lyr(NUTS3_vector_path,
                                                   strd_raster_path_full, 
                                                   temp_path, NUTS3_feat_id_LIST
                                                   , MOST_RECENT_CUT)
                    
                    
    for f_ in os.listdir("%s/%s" %(p_, sd)):
        if f_.endswith(".tif"):
            fn.append("%s/%s/%s" %(p_, sd, f_))
            print(f_)
            if "g100_clc12_v18_5" in f_.lower():
                data, geotransform_obj = CRL.clip_raster_layer(fn[-1]
                                            , REFERENCE_geotransform_obj
                                            , REFERENCE_RasterSize)
                data2 = np.zeros((data.shape),dtype="f4")
                data3 = np.zeros_like(data2)
                data4 = np.ones_like(data2) * 10.0 # 1000 m2
                data2[data <= 21] = 10.0
                data3[data <= 6] = 10.0
                data3[data == 9] = 10.0
                data3[data == 10] = 10.0
                data3[data == 11] = 10.0
                data3[data == 20] = 10.0
                print(np.sum(data2))
                print(np.sum(data3))
                print(np.sum(data4))
                
                
            elif "ESM100m_final" in f_:   
                data5, geotransform_obj = CRL.clip_raster_layer(fn[-1]
                                            , REFERENCE_geotransform_obj
                                            , REFERENCE_RasterSize)
                data5 *= 10.0/100.0 # in 1000 m2, data5 Einheit = %
                print(np.sum(data5))
    
    
    
    print(time.time() - st)
    ARR_NUTS_ID_NUMBER, geotransform_obj = SF.rrl("%s/%s_id_number.tif" %(prepro_path, "NUTS3"), data_type="uint16")
    print(time.time() - st)
    ARR_LAU2_ID_NUMBER, geotransform_obj = SF.rrl("%s/%s_id_number.tif" %(prepro_path, "LAU2"), data_type="uint32")
    print(time.time() - st)
    
    
    
    #num_fn = len(fn)
    num_fn = 4
    
    RES_Table_NUTS = np.zeros((np.max(ARR_NUTS_ID_NUMBER)+1, num_fn+1), "f4")                
    RES_Table_LAU = np.zeros((np.max(ARR_LAU2_ID_NUMBER)+1, num_fn+1), "f4")  
    RES_Table_NUTS[:,0] = np.arange(RES_Table_NUTS.shape[0])
    RES_Table_LAU[:,0] = np.arange(RES_Table_LAU.shape[0])
    
    header = ["DI"]
    #for i, f_ in enumerate(fn):
    for i  in range(num_fn):
        #print(f_)
        
        if i == 0:
            data = data2.copy()
            fn = "dauersiedlungsraum"
        elif i == 1:
            data = data3.copy()
            fn = "dauersiedlungsraum_eng" 
        elif i == 2:
            data = data4.copy()
            fn = "flaeche"
        else:
            data = data5.copy()
            fn = "ESM100m_final"
        print(fn)
        header.append(fn)  
        print(np.sum(data))
        #header.append(f_.split("/")[-1])  
        #data, geotransform_obj = SF.rrl(f_, data_type=data_type)
        
        TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(data, ARR_NUTS_ID_NUMBER) 
        print(time.time() - st)
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(data, ARR_LAU2_ID_NUMBER) 
        del data
        print(time.time() - st)
        RES_Table_NUTS[:, i+1] = TABLE_RESULTS_NUTS[:,-1]
        RES_Table_LAU[:, i+1] = TABLE_RESULTS_LAU[:,-1]
        #break
    
    header = ",".join(header)
    np.savetxt("%s/%s.csv" %(prepro_path, "__TABLE_RES_LAU2"), np.round(RES_Table_LAU, 3), delimiter=",", header=header, comments="")
    np.savetxt("%s/%s.csv" %(prepro_path, "__TABLE_RES_NUTS"), np.round(RES_Table_NUTS, 3), delimiter=",", header=header, comments="")
    
    print("DONE")