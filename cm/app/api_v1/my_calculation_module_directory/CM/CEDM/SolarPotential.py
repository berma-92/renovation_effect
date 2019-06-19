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
import  CM_intern.CEDM.modules.higherRes as hr 
import CM_intern.CEDM.modules.cyf.create_density_map as CDM

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

        
        fn_NUTSID_map = "%s/NUTS3_id_number.tif" % self.preproccessed_input_path
        fn_LAUID_map = "%s/LAU2_id_number.tif" % self.preproccessed_input_path
        
        fn_footprint_esm_share = "%s/_____ESM100m_final.tif" % self.raw_input_data_path
        fn_footprint_osm = "%s/_____0__FINAL_OSMbuildings_FOOTPRINT.tif" % self.preproccessed_input_path
        #self.rel_CDD = "%s/HDD_CDD_data_new/CDD_EnergyIntensityIndicator.tif" % self.preproccessed_input_path 
        
        fn_HDD = "%s/HDD_CDD_data_new/HDD_FINAL.tif" % self.preproccessed_input_path
        
        
        fn_solar_radiation = "%s/solar_radiation/climate_solar_radiation/data/output_solar_radiation.tif" % self.raw_input_data_path
        fn_corine_landuse = "%s/g100_clc12_V18_5.tif" % self.raw_input_data_path
        
        
        assert os.path.exists(fn_NUTSID_map)
        assert os.path.exists(fn_LAUID_map)
        assert os.path.exists(fn_footprint_esm_share)
        assert os.path.exists(fn_footprint_osm)
        assert os.path.exists(fn_solar_radiation)
        assert os.path.exists(fn_corine_landuse)

        
        self.datatype_int = 'int32'
        self.datatype = 'f4'
        self.noDataValue = 0
        
        
        
        NUTSID_map, geotransform_obj = SF.rrl(fn_NUTSID_map, data_type=self.datatype)  
        
        REFERENCE_RasterSize = NUTSID_map.shape
        
        solar_radiation, geotransform_obj_solar = SF.rrl(fn_solar_radiation, data_type=self.datatype)


        
        solar_radiation, geotransform_obj_clip = CRL.clip_raster_layer([solar_radiation, geotransform_obj_solar]
                                            , geotransform_obj
                                            , REFERENCE_RasterSize)
        
        hdd, geotransform_obj_clip = CRL.clip_raster_layer(fn_HDD
                                            , geotransform_obj
                                            , REFERENCE_RasterSize)
        
        solar_radiation_ = np.zeros_like(solar_radiation)
        is_not_nan_ = np.isnan(solar_radiation) == False
        solar_radiation_[is_not_nan_] = solar_radiation[is_not_nan_]
        
        footprint_esm_share, geotransform_obj_clip = CRL.clip_raster_layer(fn_footprint_esm_share
                                            , geotransform_obj
                                            , REFERENCE_RasterSize)
        
        footprint_osm_share, geotransform_obj_clip = CRL.clip_raster_layer(fn_footprint_osm
                                            , geotransform_obj
                                            , REFERENCE_RasterSize)
        footprint = np.maximum(footprint_esm_share * 10000. / 100., footprint_osm_share)
        
        del footprint_esm_share
        del footprint_osm_share
        
        corine_land_use, geotransform_obj_clip = CRL.clip_raster_layer(fn_corine_landuse
                                            , geotransform_obj
                                            , REFERENCE_RasterSize)
        
        
        delta_eff = np.maximum(-0.05, np.minimum(0.03, (3000 - hdd) / 2000 * 0.05)) 
        
        efficiency = 0.38
        max_sol_area_per_roof_area = 0.25
        max_sol_area_per_plot_area = 0.25
        
        corine_ids_to_use_list = [12,18,19,20,21,22,29,32]
        
        idx = np.zeros(corine_land_use.shape)
        #idx[:,:] = 0
        for i in corine_ids_to_use_list:
            idx = np.logical_or(idx, corine_land_use == i)
        
        energy_open_field = solar_radiation * max_sol_area_per_plot_area * (efficiency + delta_eff) * np.maximum(0, 10000.0 - footprint * 5.0) / 1000.0 # MWh / px(ha)
        energy_open_field[idx == False] = 0
        
        energy_roof_top = solar_radiation * max_sol_area_per_roof_area * (efficiency + delta_eff) / 1000.0
        energy_roof_top *=  footprint

        SaveLayerDict = {}
        
        SaveLayerDict["footprint"] =   [("%s/%s.tif" %(self.results_data_path, "RESULTS_BUILDING_FOOTPRINT"))
                                                  , geotransform_obj
                                                  , self.datatype
                                                  , footprint, self.noDataValue]
        
        SaveLayerDict["energy_open_field"] =   [("%s/%s.tif" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_OPENFIELD"))
                                                  , geotransform_obj
                                                  , self.datatype
                                                  , energy_open_field, self.noDataValue]
        SaveLayerDict["energy_roof_top"] =   [("%s/%s.tif" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_ROOFTOP"))
                                                  , geotransform_obj
                                                  , self.datatype
                                                  , energy_roof_top, self.noDataValue]
        
        SaveLayerDict = expLyr(SaveLayerDict)
        

        TABLE_RESULTS_NUTS_openfield = CDM.CreateResultsTableperIndicator(energy_open_field, NUTSID_map) 
        TABLE_RESULTS_NUTS_rooftop = CDM.CreateResultsTableperIndicator(energy_roof_top, NUTSID_map) 
        TABLE_RESULTS_NUTS_BUILDING_FOOTPRINT = CDM.CreateResultsTableperIndicator(footprint, NUTSID_map) 
    
    
        LAUID_map, geotransform_obj = SF.rrl(fn_LAUID_map, data_type=self.datatype)
        TABLE_RESULTS_LAU_openfield = CDM.CreateResultsTableperIndicator(energy_open_field, LAUID_map) 
        TABLE_RESULTS_LAU_rooftop = CDM.CreateResultsTableperIndicator(energy_roof_top, LAUID_map) 
        TABLE_RESULTS_LAU_BUILDING_FOOTPRINT = CDM.CreateResultsTableperIndicator(footprint, NUTSID_map)
    
        
        header =["_ID_", "VALUE"]
        
        header = ",".join(header)
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_OPENFIELD__TABLE_RES_LAU2"), 
                    np.round(TABLE_RESULTS_LAU_openfield, 3), delimiter=",", header=header, comments="")
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_ROOFTOP__TABLE_RES_LAU2"), 
                    np.round(TABLE_RESULTS_LAU_rooftop, 3), delimiter=",", header=header, comments="")
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_OPENFIELD__TABLE_RES_NUTS"), 
                    np.round(TABLE_RESULTS_NUTS_openfield, 3), delimiter=",", header=header, comments="")
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_ENERGY_SOLARTHERM_ROOFTOP__TABLE_RES_NUTS"), 
                    np.round(TABLE_RESULTS_NUTS_rooftop, 3), delimiter=",", header=header, comments="")
        
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_BUILDING_FOOTPRINT__TABLE_RES_LAU2"), 
                    np.round(TABLE_RESULTS_LAU_BUILDING_FOOTPRINT, 3), delimiter=",", header=header, comments="")
        np.savetxt("%s/%s.csv" %(self.results_data_path, "RESULTS_BUILDING_FOOTPRINT__TABLE_RES_NUTS"), 
                    np.round(TABLE_RESULTS_NUTS_BUILDING_FOOTPRINT, 3), delimiter=",", header=header, comments="")
        
        
        print("DONE SOLAR_RASTER")
            
            
        
    
        
   
    
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
    
