import os
import sys
#import panda as pd


#path = os.path.dirname(os.path.abspath(__file__))
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD




""" Entry point of the calculation module function"""
if path not in sys.path:
    sys.path.append(path)
    
try:
    from ..helper import generate_output_file_tif
    from ..helper import generate_output_file_csv
    from ..helper import create_zip_shapefiles
except:
    pass
    """
    from CM.helper_functions.helper import generate_output_file_tif
    from CM.helper_functions.helper import generate_output_file_csv
    from CM.helper_functions.helper import create_zip_shapefiles
    """
#import CM.CM_TUW32.run_cm as CM32
import CM.run_cm as CM32

def create_dataframe(input_dict):
    temp = '%s' %input_dict
    temp = temp.replace("\'","\"")
    df = pd.read_json(temp, orient='records')
    return df


# %%
#def calculation(output_directory, inputs_raster_selection,inputs_vector_selection, inputs_parameter_selection):
def calculation(output_directory, inputs_raster_selection, inputs_parameter_selection):
    """ def calculation()"""
    '''
    inputs:
        

    Outputs:
        
    '''
    
    
    # ***************************** input parameters**************************
    # e.g.: sector = inputs_parameter_selection["sector"]
    
    
    # *********** # input rows from CSV DB and create dataframe***************
    # e.g.: in_df_ENERGY_BASE = create_dataframe(inputs_vector_selection['RESULTS_SHARES_2012'])
    
    
    # ************************ # Input raster files **************************
    input_raster_NUTS_id =  inputs_raster_selection["nuts_id"]
    input_raster_GFA_RES =  inputs_raster_selection["gfa_res"]
    input_raster_GFA_NRES =  inputs_raster_selection["gfa_nres"]
    input_raster_ENERGY_RES =  inputs_raster_selection["energy_res"]
    input_raster_ENERGY_NRES =  inputs_raster_selection["energy_nres"]
    input_raster_LAU2_id =  inputs_raster_selection["lau2_id"]
    input_raster_cp_share_1975 =  inputs_raster_selection["cp_share_1975"]
    input_raster_cp_share_1990 =  inputs_raster_selection["cp_share_1990"]
    input_raster_cp_share_2000 =  inputs_raster_selection["cp_share_2000"]
    input_raster_cp_share_2014 =  inputs_raster_selection["cp_share_2014"]
    
    try:
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
    except:
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
    '''
    result['name'] = 'CM District Heating Potential'
    result['indicator'] = [{"unit": "GWh", "name": "Total heat demand in GWh within the selected zone","value": total_heat_demand},
                          {"unit": "GWh", "name": "Total district heating potential in GWh within the selected zone","value": total_potential},
                          {"unit": "%", "name": "Potential share of district heating from total demand in selected zone","value": 100*round(total_potential/total_heat_demand, 4)}
                           ]
    # if graphics is not None:
    if total_potential > 0:
        output_shp2 = create_zip_shapefiles(output_directory, output_shp2)
        result["raster_layers"]=[{"name": "district heating coherent areas","path": output_raster1, "type": "custom", "symbology": [{"red":250,"green":159,"blue":181,"opacity":0.8,"value":"1","label":"DH Areas"}]}]
        result["vector_layers"]=[{"name": "shapefile of coherent areas with their potential","path": output_shp2}]
    result['graphics'] = graphics
    
    
    #TODO to create zip from shapefile use create_zip_shapefiles from the helper before sending result
    #TODO exemple  output_shpapefile_zipped = create_zip_shapefiles(output_directory, output_shpapefile)
    result = dict()
    result['name'] = 'CM Heat density divider'
    result['indicator'] = [{"unit": "KWh", "name": "Heat density total divided by  {}".format(factor),"value": str(hdm_sum)}]
    result['graphics'] = graphics
    result['vector_layers'] = vector_layers
    result['raster_layers'] = [{"name": "layers of heat_densiy {}".format(factor),"path": output_raster1} ]
    return result

    
    
    '''
    return result

if __name__ == '__main__':
        
        
        path_ = path.replace("\\", "/").split("/app/")[0]
        
        
        test_dir = '%s/tests/data/' % path_
        
        raster_file_dir = '%s/input/' % test_dir
        
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
        inputs_raster_selection["nuts_id"] = raster_file_path1
        inputs_raster_selection["gfa_res"] = raster_file_path2
        inputs_raster_selection["energy_res"] = raster_file_path3
        inputs_raster_selection["gfa_nres"] = raster_file_path2b
        inputs_raster_selection["energy_nres"] = raster_file_path3b
        
        inputs_raster_selection["lau2_id"] = raster_file_path4
        inputs_raster_selection["cp_share_1975"] = raster_file_path5
        inputs_raster_selection["cp_share_1990"] = raster_file_path6
        inputs_raster_selection["cp_share_2000"] = raster_file_path7
        inputs_raster_selection["cp_share_2014"] = raster_file_path8
        
        inputs_parameter_selection['scenario'] = "Scenario 1"
        inputs_parameter_selection['target_year'] = "2030"
        inputs_parameter_selection['red_area_77'] = "100"
        inputs_parameter_selection['red_area_80'] = "100"
        inputs_parameter_selection['red_area_00'] = "100"
        inputs_parameter_selection['red_sp_ene_77'] = "100"
        inputs_parameter_selection['red_sp_ene_80'] = "100"
        inputs_parameter_selection['red_sp_ene_00'] = "100"
        
        
        
        output_directory = test_dir + "/output"
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        calculation(output_directory, inputs_raster_selection, inputs_parameter_selection)
        