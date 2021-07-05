import os
import sys
import shutil
import configparser

import glob
import traceback

from datetime import datetime



#path = os.path.dirname(os.path.abspath(__file__))
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD

# for local run
verbose = False

""" Entry point of the calculation module function"""
if path not in sys.path:
    sys.path.append(path)

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
    print(inputs_raster_selection.keys())
    
    
    #input_raster_COUNTRY_id =  inputs_raster_selection["country_id_number"]
    input_raster_COUNTRY_id = 1
    input_raster_NUTS_id =  inputs_raster_selection["nuts_id_number"]
    input_raster_LAU2_id =  inputs_raster_selection["lau2_id_number"]
    input_raster_GFA_RES =  inputs_raster_selection["gfa_res_curr_density"]
    input_raster_GFA_NRES =  inputs_raster_selection["gfa_nonres_curr_density"]
    input_raster_ENERGY_RES =  inputs_raster_selection["heat_res_curr_density"]
    input_raster_ENERGY_NRES =  inputs_raster_selection["heat_nonres_curr_density"]
    
    
    try:
        popraster_exists = False
        input_raster_POPULATION =  inputs_raster_selection["pop_tot_curr_density"]
        print("input_raster_POPULATION 1" )
        assert (os.path.exists(inputs_raster_selection["pop_tot_curr_density"]))
        popraster_exists = True
    except:
        # This is a temporal fix
        input_raster_POPULATION = inputs_raster_selection["gfa_res_curr_density"]
        print("input_raster_POPULATION 2" )
        
    #input_raster_POPULATION = inputs_raster_selection["gfa_res_curr_density"]
    
    input_raster_cp_share_1975 =  inputs_raster_selection["ghs_built_1975_100_share"]
    input_raster_cp_share_1990 =  inputs_raster_selection["ghs_built_1990_100_share"]
    input_raster_cp_share_2000 =  inputs_raster_selection["ghs_built_2000_100_share"]
    input_raster_cp_share_2014 =  inputs_raster_selection["ghs_built_2014_100_share"]
    
    
    try:
        BUILDING_FOOTPRINT =  inputs_raster_selection["building_footprint_tot_curr"]
        print("BUILDING_FOOTPRINT 1" )
        #input_raster_POPULATION = inputs_raster_selection["RESULTS_BUILDING_FOOTPRINT"]
    except:
        # This is a temporal fix
        BUILDING_FOOTPRINT = inputs_raster_selection["gfa_res_curr_density"]
        print("BUILDING_FOOTPRINT 2" )
    
    for key_ in inputs_raster_selection.keys():
        print("%s File (%s) exists: %s" %
              (key_, inputs_raster_selection[key_], os.path.exists(inputs_raster_selection[key_])))
        
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
    
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    result = dict()
    
    
    try:
        if "new_constructions" not in inputs_parameter_selection.keys():
            inputs_parameter_selection["new_constructions"] = "No new buildings"
            result['indicator'] = [{"unit": " ", "name": "CM main no new construction" ,"value": "0"}]

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
                  BUILDING_FOOTPRINT,
                  input_raster_POPULATION, 
                  output_raster_files, 
                  output_csv_result
                  )
        #result['indicator'] = [{"unit": " ", "name": "CM main ok 22" ,"value": "0"}]
        #return(result)
    except Exception as e:
        RESULTS = {}
        RESULTS["Done"] = False
        RESULTS["ERROR"] = str(e)
        traceback.print_exc(file=sys.stdout)
        print(e)
        return(result)
    if "target_year" not in RESULTS.keys():
        RESULTS["target_year"] = 0
 
         
    # %%
    # here you should also define the symbology for the output raster
    
    result['name'] = CM_NAME + ", Target year {}".format(RESULTS["target_year"])
    if "Done" not in RESULTS.keys() or RESULTS['Done'] == False:
        result['indicator'] = [{"unit": " ", "name": "Some unkown / unhandeld ERROR occured. We sincerely apologize." ,"value": "0"}]
        result['indicator'].append({"unit": " ", "name": "Error message: -- %s --" %RESULTS["ERROR"] ,"value": "0"})   
    elif "ERRORNOBUILDINGDATA" in RESULTS.keys():
        result['indicator'] = [{"unit": "--", "name": "ERROR: %s" % RESULTS["ERRORNOBUILDINGDATA"],"value": "%4.0f" % 0}]
    elif "ERRORSIZE" in RESULTS.keys():
        result['indicator'] = [{"unit": "%", "name": "ERROR: %s - Max. allowed area exceeded by factor of " % RESULTS["ERRORSIZE"],"value": "%4.0f" % (RESULTS["size"] * 100)}]
    
    else:
        try:
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
            
            result['indicator'] = [
                {"unit": "", "name": "Underlying population growth assumptions 2015 - ","value": "%i" % target_yr}]
            
            if popraster_exists == True:
                result['indicator'].extend([{"unit": "tds. people", "name": "Population 2000","value": "%4.2f" % RESULTS["pop_2000"]}, 
                                      {"unit": "tds. people", "name": "Population 2005","value": "%4.2f" % RESULTS["pop_2005"]},  
                                      {"unit": "tds. people", "name": "Population 2010","value": "%4.2f" % RESULTS["pop_2010"]},
                                      {"unit": "tds. people", "name": "Population 2015","value": "%4.2f" % RESULTS["pop_base"]}, 
                                      {"unit": "tds. people", "name": "Population %i" %target_yr,"value": "%4.2f" % RESULTS["pop_fut"]}])
            else:
                result['indicator'].extend([{"unit": "-", "name": "Population: 2000 / 2010","value": "%4.2f" % (RESULTS["pop_2000"] / RESULTS["pop_2010"])}, 
                                      {"unit": "-", "name": "Population: 2005 / 2010","value": "%4.2f" % (RESULTS["pop_2005"] / RESULTS["pop_2010"])},  
                                      {"unit": "-", "name": "Population: 2010 / 2010","value": "%4.2f" % (RESULTS["pop_2010"] / RESULTS["pop_2010"])},
                                      {"unit": "-", "name": "Population: 2015 / 2010","value": "%4.2f" % (RESULTS["pop_base"] / RESULTS["pop_2010"])}, 
                                      {"unit": "-", "name": "Population: %i / 2010" %target_yr,"value": "%4.2f" % (RESULTS["pop_fut"] / RESULTS["pop_2010"])}])
                
            result['indicator'].extend([
                {"unit": unit_area, "name": "Heated Area in 2014","value": "%4.2f" % (RESULTS["gfa_cur"] * converter_area)},
                {"unit": unit_area, "name": "Heated residential Area in 2014","value": "%4.2f" % (RESULTS["gfa_cur_res"] * converter_area)},
                {"unit": unit_area, "name": "Heated non-residential Area in 2014","value": "%4.2f" % (RESULTS["gfa_cur_nres"] * converter_area)},

                {"unit": unit_area, "name": "Heated Area in %i" % target_yr,"value": "%4.2f" % (RESULTS["gfa_fut"] * converter_area)},
                {"unit": unit_area, "name": "Heated residential Area in %i" % target_yr,"value": "%4.2f" % (RESULTS["gfa_fut_res"] * converter_area)},
                {"unit": unit_area, "name": "Heated non-residential Area in %i" % target_yr,"value": "%4.2f" % (RESULTS["gfa_fut_nres"] * converter_area)},

                {"unit": "m2/capita", "name": "Heated area per capita 2015","value": "%4.2f" % RESULTS["gfa_per_cap_cur"]},
                {"unit": "m2/capita", "name": "Heated area per capita %i"%target_yr,"value": "%4.2f" % RESULTS["gfa_per_cap_fut"]},
                {"unit": unit_energy, "name": "Energy Consumption in 2014","value": "%4.2f" % (RESULTS["ene_cur"] * converter_ene)},
                {"unit": unit_energy, "name": "Energy Consumption in %i" % target_yr,"value": "%4.2f" % (RESULTS["ene_fut"] * converter_ene)},
                {"unit": "kWh/m2", "name": "Current specific Energy Consumption","value": "%4.1f" % RESULTS["spe_ene_cur"]},
                {"unit": "kWh/m2", "name": "SpecificEnergy Consumption in %i" % target_yr,"value": "%4.1f" % RESULTS["spe_ene_fut"]},
                ])
            
            
            result['indicator'].extend([{"unit": "", "name": "Estimated Area per Constr. Period in","value": "2014"},
                                  {"unit": unit_area, "name": "    until 1975","value": "%4.2f" % (RESULTS["gfa_75_cur"] * converter_area)},
                                  {"unit": unit_area, "name": "     1976-1990","value": "%4.2f" % (RESULTS["gfa_80_cur"] * converter_area)},
                                  {"unit": unit_area, "name": "     1990-2014","value": "%4.2f" % (RESULTS["gfa_00_cur"] * converter_area)},
                                  {"unit": "", "name": "Estimated Area per Constr. Period in","value": "%s"% target_yr},
                                  {"unit": unit_area, "name": "    until 1975","value": "%4.2f" % (RESULTS["gfa_75_fut"] * converter_area)},
                                  {"unit": unit_area, "name": "     1976-1990","value": "%4.2f" % (RESULTS["gfa_80_fut"] * converter_area)},
                                  {"unit": unit_area, "name": "     1990-2014","value": "%4.2f" % (RESULTS["gfa_00_fut"] * converter_area)},
                                  {"unit": unit_area, "name": "     2015-%s"%target_yr,"value": "%4.2f" % (RESULTS["gfa_new_fut"] * converter_area)},
                                  {"unit": "", "name": "Estimated Energy per Constr. Period in","value": "2014"},
                                  {"unit": unit_energy, "name": "    until 1975","value": "%4.2f" % (RESULTS["ene_75_cur"] * converter_ene)},
                                  {"unit": unit_energy, "name": "     1976-1990","value": "%4.2f" % (RESULTS["ene_80_cur"] * converter_ene)},
                                  {"unit": unit_energy, "name": "     1990-2014","value": "%4.2f" % (RESULTS["ene_00_cur"] * converter_ene)},
                                  {"unit": "", "name": "Estimated Energy per Constr. Period in","value": "%s"% target_yr},
                                  {"unit": unit_energy, "name": "    until 1975","value": "%4.2f" % (RESULTS["ene_75_fut"] * converter_ene)},
                                  {"unit": unit_energy, "name": "     1976-1990","value": "%4.2f" % (RESULTS["ene_80_fut"] * converter_ene)},
                                  {"unit": unit_energy, "name": "     1990-2014","value": "%4.2f" % (RESULTS["ene_00_fut"] * converter_ene)},
                                  {"unit": unit_energy, "name": "     2015-%s"%target_yr,"value": "%4.2f" % (RESULTS["ene_new_fut"] * converter_ene)},
                                  {"unit": "", "name": "Estimated specific Energy Consumption per Constr. Period in","value": "2014"},
                                  {"unit": "kWh/m2", "name": "    until 1975","value": "%4.0f" % RESULTS["spec_ene_75_cur"]},
                                  {"unit": "kWh/m2", "name": "     1976-1990","value": "%4.0f" % RESULTS["spec_ene_80_cur"]},
                                  {"unit": "kWh/m2", "name": "     1990-2014","value": "%4.0f" % RESULTS["spec_ene_00_cur"]},
                                  {"unit": "", "name": "Estimated specific Energy Consumption per Constr. Period in","value": "%s"% target_yr},
                                  {"unit": "kWh/m2", "name": "    until 1975","value": "%4.0f" % RESULTS["spec_ene_75_fut"]},
                                  {"unit": "kWh/m2", "name": "     1976-1990","value": "%4.0f" % RESULTS["spec_ene_80_fut"]},
                                  {"unit": "kWh/m2", "name": "     1990-2014","value": "%4.0f" % RESULTS["spec_ene_00_fut"]},
                                   ])
            
            if RESULTS["spec_ene_new_fut"] > 0 and RESULTS["spec_ene_new_fut"] < 500:
                result['indicator'].append({"unit": "kWh/m2", "name": "     2015-%s"%target_yr,"value": "%4.0f" % RESULTS["spec_ene_new_fut"]})
            
            result['indicator'].append({"unit": "%", "name": "Share of newly constructed buildings shown in map in %i"%target_yr,"value": "%4.1f" % RESULTS["share_of_new_constructions_shown_in_map"]})
            
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
                                            "label": "Heated Gross Floor Area %i versus %i" %(base_yr, target_yr),
                                            "backgroundColor": ["#b03a2e", "#f1948a", "#6c3483", "#bb8fce", "#2874a6", " #85c1e9 ", "#239b56", "#82e0aa"],
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
                                            "label": "Energy Consumption for Heating and Domestic Hot Water Preparation %i versus %i" %(base_yr, target_yr),
                                            "backgroundColor": ["#b03a2e", "#f1948a", "#6c3483", "#bb8fce", "#2874a6", " #85c1e9 ", "#239b56", "#82e0aa"],
                                            "data": [RESULTS["ene_75_cur"] * converter_ene, RESULTS["ene_75_fut"] * converter_ene,
                                                     RESULTS["ene_80_cur"] * converter_ene, RESULTS["ene_80_fut"] * converter_ene,
                                                     RESULTS["ene_00_cur"] * converter_ene, RESULTS["ene_00_fut"] * converter_ene,
                                                     RESULTS["ene_new_cur"] * converter_ene, RESULTS["ene_new_fut"] * converter_ene]
                                            }]
                            }
                    }]
            result['graphics'] = graphics
            
            new_construction_methode = inputs_parameter_selection["new_constructions"].lower().strip()
            if new_construction_methode.startswith("no"):
                mnb = "no"
            elif new_construction_methode.startswith("replace"):
                mnb = "replace only"
            elif new_construction_methode.startswith("add"):
                mnb = "all"
            else: 
                mnb =""
                
            result["raster_layers"] =[
                                {"name": "Energy Consumption (Buildings constr. after 2014: %s) in %i (%s)" % (mnb, target_yr, date_time),
                                        "path": output_raster_files["output_raster_energy_tot"], "type": "heat"}
                            ,   {"name": "Heated gross floor area (Buildings constr. after 2014: %s) in %i (%s)" % (mnb, target_yr, date_time),
                                        "path": output_raster_files["output_raster_gfa_tot"], "type": "gross_floor_area"}
                            ]
                            # ,   {"name": "Energy Consumption in %i compared to 2014" % target_yr,"path": output_raster_files["output_raster_gfa_tot"], "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"Energy Consumption of (excl. buildings constructed after 2014) in %i"% target_yr}]}
                            # ,   {"name": "Heated gross floor area in %i" % target_yr,"path": output_raster_files["output_raster_gfa_tot"], "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"Heated gross floor area (excl. buildings constructed after 2014) in %i"% target_yr}]}
                            #    ]

        except Exception as e:
            result['indicator'] = [{"unit": " ", "name": "Some unkown / unhandeld ERROR occured in the results handling. We sincerely apologize." ,"value": "0"}]
            result['indicator'].append({"unit": " ", "name": "Error message: %s" %str(e) ,"value": "0"})
    
    
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

    if True:
        with open("%s/indicators_exact.csv" % (output_directory), "w") as fn:
            string_ = "%s\n" % (result['name'])
            fn.write(string_)
            print(string_)

            for ele in RESULTS.keys():
                r = RESULTS[ele]
                string_ = "%s,%s" % (ele, r)
                fn.write("%s\n" % string_)
                print(string_)

    return result

def modProjectPath(path):
    proj_path = os.getcwd().split('projects2')
    return os.path.join(proj_path[0],path)

if __name__ == '__main__':
    configfile_location = 'calculation_module_conf.ini'
    config = configparser.ConfigParser()
    if not config.read(configfile_location):
        raise AttributeError("Couldn't load configuration file ",
                             configfile_location)
    if config['machine']['machine'] == 'server':
        input_paths_label = 'proj_path_' + 'server'
        proj_path = modProjectPath(config[input_paths_label]['proj_path'])
    elif config['machine']['machine'] == 'local':
        input_paths_label = 'proj_path_' + 'local'
        proj_path = str(config[input_paths_label]['proj_path'])
    else:
        raise AttributeError("No selected machine in configuration file")

    data_warehouse = os.path.join(proj_path, config['input_paths']['data_warehouse'])
    outdir_name = config['input_paths']['outdir_name']

    if not os.path.exists(data_warehouse):
        raise FileNotFoundError(data_warehouse)

    skipped_folders = []

    #for directory, dirnames, filenames in os.walk(data_warehouse):
    #    for dirname in dirnames:
    #        if dirname == outdir_name:
    #            shutil.rmtree(os.path.join(directory, dirname))

    for region in os.listdir(data_warehouse):
        directory = os.path.join(data_warehouse, region)
        try:
            raster_file_dir = directory

            #raster_file_path0 = os.path.join(raster_file_dir,str(config['input_filename']['country_id_number']))
            raster_file_path1 = os.path.join(raster_file_dir,str(config['input_filename']['nuts_id_number']))
            raster_file_path2 = os.path.join(raster_file_dir,str(config['input_filename']['gfa_res_curr_density']))
            raster_file_path3 = os.path.join(raster_file_dir,str(config['input_filename']['heat_res_curr_density']))
            raster_file_path2b = os.path.join(raster_file_dir,str(config['input_filename']['gfa_nonres_curr_density']))
            raster_file_path3b = os.path.join(raster_file_dir,str(config['input_filename']['heat_nonres_curr_density']))
            
            raster_file_path4 = os.path.join(raster_file_dir,str(config['input_filename']['lau2_id_number']))
            raster_file_path5 = os.path.join(raster_file_dir,str(config['input_filename']['GHS_BUILT_1975_100_share']))
            raster_file_path6 = os.path.join(raster_file_dir,str(config['input_filename']['GHS_BUILT_1990_100_share']))
            raster_file_path7 = os.path.join(raster_file_dir,str(config['input_filename']['GHS_BUILT_2000_100_share']))
            raster_file_path8 = os.path.join(raster_file_dir,str(config['input_filename']['GHS_BUILT_2014_100_share']))
            raster_file_path9 = os.path.join(raster_file_dir,str(config['input_filename']['building_footprint_tot_curr'])) 
            raster_file_path10 = os.path.join(raster_file_dir,str(config['input_filename']['pop_tot_curr_density'])) 

            inputs_raster_selection = {}
            inputs_parameter_selection = {}
            inputs_vector_selection = {}
            #inputs_raster_selection["country_id_number"] = raster_file_path0
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
            inputs_raster_selection["building_footprint_tot_curr"] = raster_file_path9
            inputs_raster_selection["pop_tot_curr_density"] = raster_file_path10

            inputs_parameter_selection['red_area_77'] = str(config['inputs_parameter_selection']['red_area_77'])
            inputs_parameter_selection['red_area_80'] = str(config['inputs_parameter_selection']['red_area_80'])
            inputs_parameter_selection['red_area_00'] = str(config['inputs_parameter_selection']['red_area_00'])
            inputs_parameter_selection['red_sp_ene_77'] = str(config['inputs_parameter_selection']['red_sp_ene_77'])
            inputs_parameter_selection['red_sp_ene_80'] = str(config['inputs_parameter_selection']['red_sp_ene_80'])
            inputs_parameter_selection['red_sp_ene_00'] = str(config['inputs_parameter_selection']['red_sp_ene_00'])
            inputs_parameter_selection['add_population_growth'] = str(config['inputs_parameter_selection']['add_population_growth'])
            inputs_parameter_selection['new_constructions'] = str(config['inputs_parameter_selection']['new_constructions'])
            inputs_parameter_selection['scenarios_path'] = os.path.join(proj_path,
                                                                        config['input_paths']['scenarios'])

            fl = os.path.join(proj_path, config['input_paths']['scenarios'], "*RESULTS_ENERGY_*.csv")
            fl = glob.glob(fl)
            fl.sort()
            #print("There are %i scenario .csv file(s) in scenario directory." % len(fl))
            available_scenarios = {}
            available_years = []
            for ele in fl:
                ele = os.path.split(ele)[1].split('_RESULTS_ENERGY_')
                scen = ele[0]
                yr = ele[1].replace('.csv','')
                try: 
                    yr_int = int(yr)
                    if yr_int > 2015:
                        if scen not in available_scenarios.keys():
                            available_scenarios[scen] = []
                        available_scenarios[scen].append(yr)
                        available_years.append(str(yr))
                except:
                    pass
            scenario_list= list(available_scenarios.keys())
            year_list = sorted(list(set(available_years)))
            if config['inputs_parameter_selection']['specific'] == 'True':
                inputs_parameter_selection['scenario'] = str(config['inputs_parameter_selection']['scenario'])
                inputs_parameter_selection['target_year'] = str(config['inputs_parameter_selection']['target_year'])
                output_directory = os.path.join(directory, outdir_name)
                if not os.path.exists(output_directory):
                    os.mkdir(output_directory)
                else:
                    shutil.rmtree(output_directory)

                result = calculation(output_directory, inputs_raster_selection, inputs_parameter_selection,
                            direct_call_calc_mdoule=True)
            if config['inputs_parameter_selection']['specific'] == 'False':
                for scenario in scenario_list:
                    for year in year_list:
                        outdir_name = str(scenario) + '_' + str(year)
                        output_directory = os.path.join(directory,outdir_name)
                        inputs_parameter_selection['scenario'] = scenario
                        inputs_parameter_selection['target_year'] = year
                        if not os.path.exists(output_directory):
                            os.mkdir(output_directory)
                        else:
                            shutil.rmtree(output_directory)
                            os.mkdir(output_directory)
                        result = calculation(output_directory, inputs_raster_selection, inputs_parameter_selection,
                                    direct_call_calc_mdoule=True)
                    #DEBUG BREAK
                    #break

            else:
                raise IOError('Change in config file section "inputs_parameter_selection" variable "section" to "True"'
                              'or "False"')
        except:
            skipped_folders.append(directory)
        # DEBUG BREAK
        #break
    print("#"*50)
    print(skipped_folders)