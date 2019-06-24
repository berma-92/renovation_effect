import os
import sys
path = os.path.dirname(os.path.abspath(__file__))
from ..helper import generate_output_file_tif
from ..helper import generate_output_file_csv
from ..helper import create_zip_shapefiles
""" Entry point of the calculation module function"""
if path not in sys.path:
    sys.path.append(path)
import my_calculation_module_directory.CM.CM_TUW32.run_cm as CM32


def create_dataframe(input_dict):
    temp = '%s' %input_dict
    temp = temp.replace("\'","\"")
    df = pd.read_json(temp, orient='records')
    return df


# %%
#def calculation(output_directory, inputs_raster_selection,inputs_vector_selection, inputs_parameter_selection):
def calculation(output_directory, inputs_raster_selection):
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
    input_raster_ENERGY_RES =  inputs_raster_selection["energy_res"]
    input_raster_LAU2_id =  inputs_raster_selection["lau2_id"]
    input_raster_cp_share_1975 =  inputs_raster_selection["cp_share_1975"]
    input_raster_cp_share_1990 =  inputs_raster_selection["cp_share_1990"]
    input_raster_cp_share_2000 =  inputs_raster_selection["cp_share_2000"]
    input_raster_cp_share_2014 =  inputs_raster_selection["cp_share_2014"]
    
    # ************************ # Output raster files **************************
    output_raster_energy = generate_output_file_tif(output_directory)

    # ************************ # Output CSV files **************************
    output_csv_result = generate_output_file_csv(output_directory)


    CM32.main(input_raster_NUTS_id, input_raster_GFA_RES,
              input_raster_ENERGY_RES, input_raster_LAU2_id,
              input_raster_cp_share_1975, input_raster_cp_share_1990,
              input_raster_cp_share_2000, input_raster_cp_share_2014,
              output_raster_energy, output_csv_result
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
    '''
    return result