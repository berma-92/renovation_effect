'''
Created on Jul 24, 2017

@author: Andreas

run this script to calculate the energy density maps
'''
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM_intern.CEDM.calcDensity import ClassCalcDensity
from CM_intern.CEDM.Create_NUTS_LAU_indexRaster import ClassCalcNUTSLAU_raster




def main(pr_path, prj_path_input, prj_path_output
         , NUTS3_feat_id_LIST, preproccessed_input_path):
    
    #NUTS3_feat_id_LIST = list(NUTS3_feat_id_LIST)
    #"""
    
    CNLr = ClassCalcNUTSLAU_raster(pr_path, prj_path_input
                                   , prj_path_output, preproccessed_input_path)

    CNLr.main_process(NUTS3_feat_id_LIST)
    #"""
    
    CD = ClassCalcDensity(pr_path, prj_path_input, prj_path_output
                          , preproccessed_input_path)
    
    CD.main_process(NUTS3_feat_id_LIST)
    
    if len(NUTS3_feat_id_LIST) > 1.100:
        copy2GITDIR = True
    else:
        copy2GITDIR = False
    
    CD.create_sum_of_res_nres(copy2GITDIR)
    
    
    CD.create_floor_area_per_construction_period(NUTS3_feat_id_LIST, copy2GITDIR)
    
    
    return

if __name__ == "__main__":
    
    print(sys.version_info)
    print(os.getcwd())
    pr_path = "C:/Hotmaps_DATA/heat_density_map_test"
    if not os.path.exists(pr_path):
        pr_path = "../../../../../../Hotmaps_DATA/heat_density_map"
    
    prj_path_output = "output_noLAUcorr"
    #Nuts3 Regions
    NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
    
    #NUTS3_feat_id_LIST = range(14)
    #NUTS3_feat_id_LIST = range(603,615)
    #NUTS3_feat_id_LIST = range(1300,15000)
    #NUTS3_feat_id_LIST = ["DK"]
    #main(pr_path, prj_path_output, NUTS3_feat_id_LIST)
    #NUTS3_feat_id_LIST = range(500)
    #NUTS3_feat_id_LIST = range(30)
    #NUTS3_feat_id_LIST = range(10)
    #NUTS3_feat_id_LIST = [14]  
    #NUTS3_feat_id_LIST = range(100)
    #NUTS3_feat_id_LIST = range(10,15)
    prj_path_output = "output_2"
    
    prj_path_input = "Input Data"
    preproccessed_input_path = "1_inputdata_preproccessed"
    #prj_path_input =  "Input Data_cut"
    #prj_path_output = "output_test_ch"
    #NUTS3_feat_id_LIST = ["CH"]
    
        
    main(pr_path, prj_path_input, prj_path_output
         , NUTS3_feat_id_LIST, preproccessed_input_path)
    
    #start()
    print("Done!")

