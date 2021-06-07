#import time

import os, sys
import numpy as np
import glob
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD

if path not in sys.path:
    sys.path.append(path)
from CM.N3scenario_to_raster import CalcEffectsAtRasterLevel
from CM.helper_functions.readCsvData import READ_CSV_DATA
from CM.helper_functions.read_raster import raster_array as RA
#import CM.helper_functions.Subfunctions as SF
#import CM.helper_functions.cliprasterlayer as CRL
#from CM.helper_functions.exportLayerDict import export_layer as expLyr


print(sys.version_info)


MAX_SIZE = 30 * 10**6
#MAX_SIZE = 30 * 10**8
BASE_YEAR = 2014
def main(inputs_parameter_selection,
         input_raster_Country_id, 
         input_raster_NUTS_id,
         input_raster_GFA_RES,
         input_raster_GFA_NRES,
         input_raster_ENERGY_RES,
         input_raster_ENERGY_NRES,
         input_raster_LAU2_id,
         input_raster_cp_share_1975,
         input_raster_cp_share_1990,
         input_raster_cp_share_2000,
         input_raster_cp_share_2014,
         input_raster_BUILDING_FOOTPRINT,
         input_raster_POPULATION,
         output_raster_files,
         output_csv_result, 
         debug_output=False):

    data_type = "f4"
    data_type_int = "uint32"
    #local_input_dir = path + "/input_data"
    local_input_dir = str(inputs_parameter_selection['scenarios_path'])
    target_year = int(inputs_parameter_selection["target_year"])
    scenario_name = inputs_parameter_selection['scenario']
    
    
    NUTS_id, gt = RA(input_raster_NUTS_id, dType="uint16", return_gt=True)
    if NUTS_id.size > (MAX_SIZE):
        RESULTS = {}
        RESULTS["ERRORSIZE"] = "Selected region is too large, please reduce the select area!"
        RESULTS["size"] =  NUTS_id.size / (MAX_SIZE)
        RESULTS["target_year"] = int(target_year)
        RESULTS["Done"] = True
        return RESULTS
    
    if debug_output == True:
        # Country_id only needed for tabular csv-results
        Country_id = RA(input_raster_Country_id, dType="uint8")
    else:
        Country_id = 1

    RESULTS = {}

    LAU2_id = RA(input_raster_LAU2_id, dType=data_type_int)
    cp_share_1975 = RA(input_raster_cp_share_1975, dType=data_type)
    cp_share_1990 = RA(input_raster_cp_share_1990, dType=data_type)
    cp_share_2000 = RA(input_raster_cp_share_2000, dType=data_type)
    cp_share_2014 = RA(input_raster_cp_share_2014, dType=data_type)
    print("cp_share_1975:{}".format(np.sum(cp_share_1975)))
    print("cp_share_1990:{}".format(np.sum(cp_share_1990)))
    print("cp_share_2000:{}".format(np.sum(cp_share_2000)))
    print("cp_share_2014:{}".format(np.sum(cp_share_2014)))
    print("Shape: cp_share_2014:{}".format(cp_share_2014.shape))
    if (np.sum(cp_share_1975) + np.sum(cp_share_1990) +
        np.sum(cp_share_2000) + np.sum(cp_share_2014)) <= 0.0001:
        RESULTS = {}
        RESULTS["ERRORNOBUILDINGDATA"] = "No building construction data for selected region!"
        RESULTS["target_year"] = int(target_year)
        RESULTS["Done"] = True
        return RESULTS



    NUTS_id_size = NUTS_id.shape
    cp_share_2000_and_2014 = cp_share_2000 + cp_share_2014
    cp_share_2000_and_2014[:,:] = np.minimum(cp_share_2000_and_2014, 1 - cp_share_1990 - cp_share_1975)
    del cp_share_2000, cp_share_2014

    #Check if target year is available for scenario
    yr_list = []
    
    fl = glob.glob(local_input_dir + "/%s_RESULTS_ENERGY_*.csv" % (scenario_name))
    fl.sort()
    for ele in fl:
        ele = ele.replace("\\","/").replace("//","/")
        ele = (ele.split("/")[-1]).split("_RESULTS_ENERGY_")
        yr = ele[1][:-4]
        yr_list.append(yr)
    yr_list.sort()
    
   
    #RESULTS["Done"] = True
    #return RESULTS
    for i in yr_list:
        if int(i) > BASE_YEAR:
            initial_yr = i
            break
    
    if not os.path.exists(local_input_dir + "/%s_RESULTS_SHARES_ENE_%i.csv" % (scenario_name, target_year)):
        target_year = yr_list[min(3, len(yr_list)-1)]
        print("Choosen Target year:{}".format(target_year))

    #RESULTS["Done"] = True
    #return RESULTS
    NUTS_RESULTS_SHARES_ENERGY_BASE = READ_CSV_DATA(local_input_dir + "/%s_RESULTS_SHARES_ENE_%s.csv"%(scenario_name, initial_yr), skip_header=3)[0]
    NUTS_RESULTS_SHARES_ENERGY_FUTURE = READ_CSV_DATA(local_input_dir + "/%s_RESULTS_SHARES_ENE_%s.csv" % (scenario_name, target_year), skip_header=3)[0]
    NUTS_RESULTS_ENERGY_FUTURE_abs = READ_CSV_DATA(local_input_dir + "/%s_RESULTS_ENERGY_%s.csv" % (scenario_name, target_year), skip_header=3)[0]
    NUTS_RESULTS_GFA_BASE = READ_CSV_DATA(local_input_dir + "/%s_RESULTS_GFA_%s.csv" % (scenario_name, initial_yr), skip_header=3)[0]
    NUTS_RESULTS_GFA_FUTURE = READ_CSV_DATA(local_input_dir + "/%s_RESULTS_GFA_%s.csv" % (scenario_name, target_year), skip_header=3)[0]
    
    NUTS_RESULTS_POPULATION = READ_CSV_DATA(local_input_dir + "/DevelopmentPopNUTS3.csv", skip_header=3)[0]
    


    csv_data_table = READ_CSV_DATA(local_input_dir + "/Communal2_data.csv", skip_header=6)
    
    
    #fn_res_bgf_initial = "%s/RESULTS_GFA_RES_BUILD.csv" % dirname

    adoption_bgf = [float(inputs_parameter_selection['red_area_77']), float(inputs_parameter_selection['red_area_80']), float(inputs_parameter_selection['red_area_00'])]
    adoption_sp_ene = [float(inputs_parameter_selection['red_sp_ene_77']), float(inputs_parameter_selection['red_sp_ene_80']), float(inputs_parameter_selection['red_sp_ene_00'])]
    add_pop_growth = float(inputs_parameter_selection['add_population_growth'])
    new_buildings_distribution_method = inputs_parameter_selection['new_constructions']
    inputs_parameters = {"scenario_name": scenario_name, 
                         "adoption_bgf": adoption_bgf,
                         "adoption_sp_ene": adoption_sp_ene,
                         "new_constructions": new_buildings_distribution_method,
                         "base_year": BASE_YEAR,
                         "target_year": int(target_year),
                         "add_pop_growth": add_pop_growth}
    #RESULTS["Done"] = True
    #return RESULTS
    RESULTS = CalcEffectsAtRasterLevel(NUTS_RESULTS_GFA_BASE,
                                    NUTS_RESULTS_GFA_FUTURE,
                                    NUTS_RESULTS_SHARES_ENERGY_BASE,
                                    NUTS_RESULTS_SHARES_ENERGY_FUTURE,
                                    NUTS_RESULTS_ENERGY_FUTURE_abs,
                                    NUTS_RESULTS_POPULATION,
                                    Country_id,
                                    NUTS_id,
                                    LAU2_id,
                                    cp_share_1975,
                                    cp_share_1990,
                                    cp_share_2000_and_2014,
                                    input_raster_BUILDING_FOOTPRINT,
                                    input_raster_ENERGY_RES,
                                    input_raster_ENERGY_NRES, 
                                    input_raster_GFA_RES,
                                    input_raster_GFA_NRES,
                                    input_raster_POPULATION, 
                                    gt,
                                    NUTS_id_size,
                                    csv_data_table,
                                    output_raster_files,
                                    output_csv_result,
                                    inputs_parameters, 
                                    debug_output=False)
    
    
    RESULTS["Done"] = True    
    RESULTS["target_year"] = int(target_year)
    return RESULTS