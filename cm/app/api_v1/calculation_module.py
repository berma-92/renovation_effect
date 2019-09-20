import os
import sys

import glob



#path = os.path.dirname(os.path.abspath(__file__))
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD

# for local run
verbose = False

""" Entry point of the calculation module function"""
if path not in sys.path:
    sys.path.append(path)
"""
try:
    from ..helper import generate_output_file_tif
    from ..helper import generate_output_file_csv
    from ..helper import create_zip_shapefiles
    from ..constant import CM_NAME
#from ..exceptions import ValidationError, EmptyRasterError
"""
CM_NAME = 'CM Effect of renovation'
#    pass
import CM.run_cm as CM32

# %%
#def calculation(output_directory, inputs_raster_selection,inputs_vector_selection, inputs_parameter_selection):
def calculation(output_directory, inputs_raster_selection, inputs_parameter_selection, direct_call_calc_mdoule=False):
    """ def calculation()"""
    '''
    inputs:
        
    Outputs:
        
    '''
    if direct_call_calc_mdoule==False:
        from ..helper import generate_output_file_tif
        from ..helper import generate_output_file_csv
        from ..helper import create_zip_shapefiles
        from ..constant import CM_NAME
    else:
        CM_NAME = 'CM Effect of renovation'
    
    # ***************************** input parameters**************************
    # e.g.: sector = inputs_parameter_selection["sector"]
    
    
    # *********** # input rows from CSV DB and create dataframe***************
    # e.g.: in_df_ENERGY_BASE = create_dataframe(inputs_vector_selection['RESULTS_SHARES_2012'])
    
    
    # ************************ # Input raster files **************************
    input_raster_COUNTRY_id =  inputs_raster_selection["country_id_number"]
    input_raster_NUTS_id =  inputs_raster_selection["nuts_id_number"]
    input_raster_LAU2_id =  inputs_raster_selection["lau2_id_number"]
    input_raster_GFA_RES =  inputs_raster_selection["gfa_res_curr_density"]
    input_raster_GFA_NRES =  inputs_raster_selection["gfa_nonres_curr_density"]
    input_raster_ENERGY_RES =  inputs_raster_selection["heat_res_curr_density"]
    input_raster_ENERGY_NRES =  inputs_raster_selection["heat_nonres_curr_density"]
    input_raster_cp_share_1975 =  inputs_raster_selection["ghs_built_1975_100_share"]
    input_raster_cp_share_1990 =  inputs_raster_selection["ghs_built_1990_100_share"]
    input_raster_cp_share_2000 =  inputs_raster_selection["ghs_built_2000_100_share"]
    input_raster_cp_share_2014 =  inputs_raster_selection["ghs_built_2014_100_share"]
    
    if direct_call_calc_mdoule==False:
        # ************************ # Output raster files **************************
        output_raster_energy_res = generate_output_file_tif(output_directory)
        output_raster_energy_nres = generate_output_file_tif(output_directory)
        output_raster_energy_res_rel = generate_output_file_tif(output_directory)
        output_raster_energy_nres_rel = generate_output_file_tif(output_directory)
        output_raster_energy_tot = generate_output_file_tif(output_directory)
        output_raster_energy_tot_rel = generate_output_file_tif(output_directory)
        
        output_raster_gfa_res = generate_output_file_tif(output_directory)
        output_raster_gfa_nres = generate_output_file_tif(output_directory)
        output_raster_gfa_res_rel = generate_output_file_tif(output_directory)
        output_raster_gfa_nres_rel = generate_output_file_tif(output_directory)
        output_raster_gfa_tot = generate_output_file_tif(output_directory)
        output_raster_gfa_tot_rel = generate_output_file_tif(output_directory)

        # ************************ # Output CSV files **************************
        output_csv_result = generate_output_file_csv(output_directory)
    else:
        # ************************ # Output raster files **************************
        
        output_raster_energy_res = "%s/Energy_RES.tif" % (output_directory)
        output_raster_energy_nres = "%s/Energy_NRES.tif" % (output_directory)
        output_raster_energy_res_rel = "%s/Energy_RES_rel.tif" % (output_directory)
        output_raster_energy_nres_rel = "%s/Energy_NRES_rel.tif" % (output_directory)
        output_raster_energy_tot = "%s/Energy_TOTAL.tif" % (output_directory)
        output_raster_energy_tot_rel = "%s/Energy_TOTAL_rel.tif" % (output_directory)
        
        output_raster_gfa_res = "%s/GFA_RES.tif" % (output_directory)
        output_raster_gfa_nres = "%s/GFA_NRES.tif" % (output_directory)
        output_raster_gfa_res_rel = "%s/GFA__RES_rel.tif" % (output_directory)
        output_raster_gfa_nres_rel = "%s/GFA__NRES_rel.tif" % (output_directory)
        output_raster_gfa_tot = "%s/GFA__TOTAL.tif" % (output_directory)
        output_raster_gfa_tot_rel = "%s/GFA__TOTAL_rel.tif" % (output_directory)
        
        # ************************ # Output CSV files **************************
        output_csv_result = output_directory + "/Results_table.csv"

    output_raster_files = {}
    output_raster_files["output_raster_energy_res"] = output_raster_energy_res
    output_raster_files["output_raster_energy_nres"] = output_raster_energy_nres
    output_raster_files["output_raster_energy_res_rel"] = output_raster_energy_res_rel
    output_raster_files["output_raster_energy_nres_rel"] = output_raster_energy_nres_rel
    output_raster_files["output_raster_energy_tot"] = output_raster_energy_tot
    output_raster_files["output_raster_energy_tot_rel"] = output_raster_energy_tot_rel
    
    output_raster_files["output_raster_gfa_res"] = output_raster_gfa_res
    output_raster_files["output_raster_gfa_nres"] = output_raster_gfa_nres
    output_raster_files["output_raster_gfa_res_rel"] = output_raster_gfa_res_rel
    output_raster_files["output_raster_gfa_nres_rel"] = output_raster_gfa_nres_rel
    output_raster_files["output_raster_gfa_tot"] = output_raster_gfa_tot
    output_raster_files["output_raster_gfa_tot_rel"] = output_raster_gfa_tot_rel
    
    
    RESULTS = CM32.main(inputs_parameter_selection,
              input_raster_COUNTRY_id,
              input_raster_NUTS_id, 
              input_raster_GFA_RES,
              input_raster_GFA_NRES,
              input_raster_ENERGY_RES, 
              input_raster_ENERGY_NRES,
              input_raster_LAU2_id,
              input_raster_cp_share_1975, input_raster_cp_share_1990,
              input_raster_cp_share_2000, input_raster_cp_share_2014,
              output_raster_files, 
              output_csv_result
              )
    
 
         
    # %%
    # here you should also define the symbology for the output raster
    result = dict()
    
    result['name'] = CM_NAME + ", Target year {}".format(RESULTS["target_year"])
    if "ERROR" in RESULTS.keys():
        result['indicator'] = [{"unit": "", "name": "ERROR:\n\n%s\n\n" % RESULTS["ERROR"],"value": ""}]
        return result
    
    target_yr = RESULTS["target_year"]
    base_yr = 2014
    if (RESULTS["gfa_75_cur"] + RESULTS["gfa_80_cur"] + RESULTS["gfa_00_cur"]) < 5000:
        unit_area = "tds. m2"
        converter_area = 1./10**3
    else:
        unit_area = "Mio. m2"
        converter_area = 1./10**6
    if (RESULTS["ene_75_cur"] + RESULTS["ene_80_cur"] + RESULTS["ene_00_cur"]) < 50 * 10**3:
        unit_energy = "MWh"
        converter_ene = 1.
    elif (RESULTS["ene_75_cur"] + RESULTS["ene_80_cur"] + RESULTS["ene_00_cur"]) > 10* 10**6:
        unit_energy = "TWh"
        converter_ene = 1./10**6
    else:
        unit_energy = "GWh"
        converter_ene = 1./10**3
        
    
    result['indicator'] = [{"unit": unit_area, "name": "Current Heated Area","value": "%4.2f" % (RESULTS["gfa_cur"] * converter_area)},
                          {"unit": unit_area, "name": "Heated Area in %i" % target_yr,"value": "%4.2f" % (RESULTS["gfa_fut"] * converter_area)},
                          {"unit": unit_energy, "name": "Current Energy Consumption","value": "%4.2f" % (RESULTS["ene_cur"] * converter_ene)},
                          {"unit": unit_energy, "name": "Energy Consumption in %i" % target_yr,"value": "%4.2f" % (RESULTS["ene_fut"] * converter_ene)},
                          {"unit": "kWh/m2", "name": "Current specific Energy Consumption","value": "%4.1f" % RESULTS["spe_ene_cur"]},
                          {"unit": "kWh/m2", "name": "SpecificEnergy Consumption in %i" % target_yr,"value": "%4.1f" % RESULTS["spe_ene_fut"]}
                            ]

    
    result['indicator'].extend([{"unit": "", "name": "\n\nCurrent data (2014)\nEstimated Area Constr. Period","value": " "},
                          {"unit": unit_area, "name": "    until 1975","value": "%4.2f" % (RESULTS["gfa_75_cur"] * converter_area)},
                          {"unit": unit_area, "name": "     1976-1990","value": "%4.2f" % (RESULTS["gfa_80_cur"] * converter_area)},
                          {"unit": unit_area, "name": "     1990-2014","value": "%4.2f" % (RESULTS["gfa_00_cur"] * converter_area)},
                          
                          {"unit": "", "name": "\n\nScenario data (%s)\nEstimated Area Constr. Period"% target_yr,"value": " "},
                          {"unit": unit_area, "name": "    until 1975","value": "%4.2f" % (RESULTS["gfa_75_fut"] * converter_area)},
                          {"unit": unit_area, "name": "     1976-1990","value": "%4.2f" % (RESULTS["gfa_80_fut"] * converter_area)},
                          {"unit": unit_area, "name": "     1990-2014","value": "%4.2f" % (RESULTS["gfa_00_fut"] * converter_area)},
                          {"unit": unit_area, "name": "     2015-%s"%target_yr,"value": "%4.2f" % (RESULTS["gfa_new_fut"] * converter_area)},
                        
                        
                          {"unit": "", "name": "\n\nCurrent data (2014)\nEstimated Energy Constr. Period","value": " "},
                          {"unit": unit_energy, "name": "    until 1975","value": "%4.2f" % (RESULTS["ene_75_cur"] * converter_ene)},
                          {"unit": unit_energy, "name": "     1976-1990","value": "%4.2f" % (RESULTS["ene_80_cur"] * converter_ene)},
                          {"unit": unit_energy, "name": "     1990-2014","value": "%4.2f" % (RESULTS["ene_00_cur"] * converter_ene)},
                          
                          {"unit": "", "name": "\n\nScenario data (%s)\nEstimated Energy Constr. Period" % target_yr,"value": " "},
                          {"unit": unit_energy, "name": "    until 1975","value": "%4.2f" % (RESULTS["ene_75_fut"] * converter_ene)},
                          {"unit": unit_energy, "name": "     1976-1990","value": "%4.2f" % (RESULTS["ene_80_fut"] * converter_ene)},
                          {"unit": unit_energy, "name": "     1990-2014","value": "%4.2f" % (RESULTS["ene_00_fut"] * converter_ene)},
                          {"unit": unit_energy, "name": "     2015-%s"%target_yr,"value": "%4.2f" % (RESULTS["ene_new_fut"] * converter_ene)},
                        
    
                        
                        {"unit": "", "name": "\n\nCurrent data (2014)\nEstimated specific Energy Consumption, Constr. Period","value": " "},
                          {"unit": "kWh/m2", "name": "    until 1975","value": "%4.0f" % RESULTS["spec_ene_75_cur"]},
                          {"unit": "kWh/m2", "name": "     1976-1990","value": "%4.0f" % RESULTS["spec_ene_80_cur"]},
                          {"unit": "kWh/m2", "name": "     1990-2014","value": "%4.0f" % RESULTS["spec_ene_00_cur"]},
                          
                        {"unit": "", "name": "\n\nScenario data (%s)\nEstimated specific Energy Consumption, Constr. Period"% target_yr,"value": " "},
                          {"unit": "kWh/m2", "name": "    until 1975","value": "%4.0f" % RESULTS["spec_ene_75_fut"]},
                          {"unit": "kWh/m2", "name": "     1976-1990","value": "%4.0f" % RESULTS["spec_ene_80_fut"]},
                          {"unit": "kWh/m2", "name": "     1990-2014","value": "%4.0f" % RESULTS["spec_ene_00_fut"]},
                           ])
    if RESULTS["spec_ene_new_fut"] > 0 and RESULTS["spec_ene_new_fut"] < 500:
        result['indicator'].append({"unit": "kWh/m2", "name": "     2015-%s"%target_yr,"value": "%4.0f" % RESULTS["spec_ene_new_fut"]})
    
    num_bars = 8   
    graphics  = [
            {
                    "type": "bar",
                    "xLabel": "Buildings per Construction Period",
                    "yLabel": "Heated Gross Floor Area [%s]" % unit_area,
                    "data": {
                            "labels": [ "until 1975 in %i" % base_yr, "until 1975 in %i" % target_yr,
                                       "1976-1990 in %i" % base_yr, "1976-1990 in %i" % target_yr,
                                       "1990-2014 in %i" % base_yr, "1990-2014 in %i" % target_yr,
                                       " after 2014 in %i" % base_yr, "after 2014 in %i" % target_yr,],
                            "datasets": [{
                                    "label": "Test1",
                                    "backgroundColor": ["#3e95cd"]*num_bars,
                                    "data": [RESULTS["gfa_75_cur"] * converter_area, RESULTS["gfa_75_fut"] * converter_area,
                                             RESULTS["gfa_80_cur"] * converter_area, RESULTS["gfa_80_fut"] * converter_area,
                                             RESULTS["gfa_00_cur"] * converter_area, RESULTS["gfa_00_fut"] * converter_area,
                                             RESULTS["gfa_new_cur"] * converter_area, RESULTS["gfa_new_fut"] * converter_area]
                                    }]
                    }
            },{
                    "type": "bar",
                    "xLabel": "Buildings per Construction Period",
                    "yLabel": "Energy Consumption for Heating [%s/yr]" % unit_energy,
                    "data": {
                            "labels": [ "until 1975 in %i" % base_yr, "until 1975 in %i" % target_yr,
                                       "1976-1990 in %i" % base_yr, "1976-1990 in %i" % target_yr,
                                       "1990-2014 in %i" % base_yr, "1990-2014 in %i" % target_yr,
                                       " after 2014 in %i" % base_yr, "after 2014 in %i" % target_yr,],
                            "datasets": [{
                                    "label": "Test1",
                                    "backgroundColor": ["#3e95cd"]*num_bars,
                                    "data": [RESULTS["gfa_75_cur"] * converter_ene, RESULTS["gfa_75_fut"] * converter_ene,
                                             RESULTS["gfa_80_cur"] * converter_ene, RESULTS["gfa_80_fut"] * converter_ene,
                                             RESULTS["gfa_00_cur"] * converter_ene, RESULTS["gfa_00_fut"] * converter_ene,
                                             RESULTS["gfa_new_cur"] * converter_ene, RESULTS["gfa_new_fut"] * converter_ene]
                                    }]
                    }
            }]
    result['graphics'] = graphics
    result["raster_layers"] =[
                        {"name": "Energy Consumption (excluding buildings constr. after 2014) in %i" % target_yr,"path": output_raster_files["output_raster_energy_tot"], "type": "heat"}
                    ,   {"name": "Heated gross floor area (excluding buildings constr. after 2014) in %i" % target_yr,"path": output_raster_files["output_raster_gfa_tot"], "type": "gross_floor_area"}
                    ]
                    # ,   {"name": "Energy Consumption in %i compared to 2014" % target_yr,"path": output_raster_files["output_raster_gfa_tot"], "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"Energy Consumption of (excl. buildings constructed after 2014) in %i"% target_yr}]}
                    # ,   {"name": "Heated gross floor area in %i" % target_yr,"path": output_raster_files["output_raster_gfa_tot"], "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"Heated gross floor area (excl. buildings constructed after 2014) in %i"% target_yr}]}
                    #    ]
    

    """
    if total_potential > 0:
        output_shp2 = create_zip_shapefiles(output_directory, output_shp2)
        result["raster_layers"]=[{"name": "district heating coherent areas","path": output_raster1, "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"DH Areas"}]}]
        result["vector_layers"]=[{"name": "shapefile of coherent areas with their potential","path": output_shp2}]
    result['graphics'] = graphics
    
    
    #TODO to create zip from shapefile use create_zip_shapefiles from the helper before sending result
    #TODO exemple  output_shpapefile_zipped = create_zip_shapefiles(output_directory, output_shpapefile)
    
    
    result['vector_layers'] = vector_layers
    result['raster_layers'] = [{"name": "layers of heat_densiy {}".format(factor),"path": output_raster1} ]
    """
    
    if direct_call_calc_mdoule == True:
        with open("%s/indicators.csv" % (output_directory), "w") as fn:
            string_ = "%s\n" %(result['name'])
            fn.write(string_)
            print(string_)
                
            for ele in range(len(result['indicator'])):
                r = result['indicator'][ele]
                string_ = "%s : %s %s" %(r['name'], str(r['value']), r["unit"])
                fn.write("%s\n"%string_)
                print(string_)

    return result



if __name__ == '__main__':
        
        
        path_ = path.replace("\\", "/").split("/app/")[0]
        
        
        test_dir = '%s/tests/data/' % path_
        
        raster_file_dir = '%s/input/' % test_dir
        
        raster_file_path0 = raster_file_dir + "/Country_cut_id_number.tif"
        raster_file_path1 = raster_file_dir + "/NUTS3_cut_id_number.tif"
        raster_file_path2 = raster_file_dir + "/RESULTS_GFA_RES_BUILD.tif"
        raster_file_path3 = raster_file_dir + "/RESULTS_ENERGY_HEATING_RES_2012.tif"
        raster_file_path2b = raster_file_dir + "/RESULTS_GFA_NRES_BUILD.tif"
        raster_file_path3b = raster_file_dir + "/RESULTS_ENERGY_HEATING_NRES_2012.tif"
        
        raster_file_path4 = raster_file_dir + "/LAU2_id_number.tif"
        raster_file_path5 = raster_file_dir + "/GHS_BUILT_1975_100_share.tif"
        raster_file_path6 = raster_file_dir + "/GHS_BUILT_1990_100_share.tif"
        raster_file_path7 = raster_file_dir + "/GHS_BUILT_2000_100_share.tif"
        raster_file_path8 = raster_file_dir + "/GHS_BUILT_2014_100_share.tif"

        """
        # simulate copy from HTAPI to CM
        save_path1 = UPLOAD_DIRECTORY+"/NUTS3_cut_id_number.tif"
        save_path2 = UPLOAD_DIRECTORY+"/RESULTS_GFA_RES_BUILD.tif"
        save_path3 = UPLOAD_DIRECTORY+"/RESULTS_ENERGY_HEATING_RES_2012.tif"
        save_path4 = UPLOAD_DIRECTORY+"/LAU2_id_number.tif"
        raster_filesave_path5 = UPLOAD_DIRECTORY+"/GHS_BUILT_1975_100_share.tif"
        save_path6 = UPLOAD_DIRECTORY+"/GHS_BUILT_1990_100_share.tif"
        save_path7 = UPLOAD_DIRECTORY+"/GHS_BUILT_2000_100_share.tif"
        save_path8 = UPLOAD_DIRECTORY+"/GHS_BUILT_2014_100_share.tif"
        
        copyfile(raster_file_path1, save_path1)
        copyfile(raster_file_path2, save_path2)
        copyfile(raster_file_path3, save_path3)
        copyfile(raster_file_path4, save_path4)
        copyfile(raster_file_path5, save_path5)
        copyfile(raster_file_path6, save_path6)
        copyfile(raster_file_path7, save_path7)
        copyfile(raster_file_path8, save_path8)
        """

        inputs_raster_selection = {}
        inputs_parameter_selection = {}
        inputs_vector_selection = {}
        inputs_raster_selection["country_id_number"] = raster_file_path0
        inputs_raster_selection["nuts_id_number"] = raster_file_path1
        inputs_raster_selection["gfa_res_curr_density"] = raster_file_path2
        inputs_raster_selection["heat_res_curr_density"] = raster_file_path3
        inputs_raster_selection["gfa_nonres_curr_density"] = raster_file_path2b
        inputs_raster_selection["heat_nonres_curr_density"] = raster_file_path3b
        
        inputs_raster_selection["lau2_id_number"] = raster_file_path4
        inputs_raster_selection["ghs_built_1975_100_share"] = raster_file_path5
        inputs_raster_selection["ghs_built_1990_100_share"] = raster_file_path6
        inputs_raster_selection["ghs_built_2000_100_share"] = raster_file_path7
        inputs_raster_selection["ghs_built_2014_100_share"] = raster_file_path8
        
        inputs_parameter_selection['scenario'] = "Scenario 1"
        inputs_parameter_selection['target_year'] = "2030"
        inputs_parameter_selection['red_area_77'] = "100"
        inputs_parameter_selection['red_area_80'] = "100"
        inputs_parameter_selection['red_area_00'] = "100"
        inputs_parameter_selection['red_sp_ene_77'] = "100"
        inputs_parameter_selection['red_sp_ene_80'] = "100"
        inputs_parameter_selection['red_sp_ene_00'] = "100"
        
        fl = glob.glob("%s/input_data/*RESULTS_ENERGY_*.csv" % path)
        fl.sort()
        print(len(fl))
        available_scenarios = {}
        for ele in fl:
            ele = ele.replace("\\","/").replace("//","/")
            ele = (ele.split("/")[-1]).split("_RESULTS_ENERGY_")
            scen = ele[0]
            yr = ele[1][:-4]
            print(scen)
            if scen not in available_scenarios.keys():
                available_scenarios[scen] = []
            available_scenarios[scen].append(yr)
            #print(ele)
            
        inputs_parameter_selection['scenario'] = "cheetah_reference_hsagent"
        inputs_parameter_selection['target_year'] = "2030"
            
        output_directory = test_dir + "/output"
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        calculation(output_directory, inputs_raster_selection, inputs_parameter_selection,
                    direct_call_calc_mdoule=True)
#'''