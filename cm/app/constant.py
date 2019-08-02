
CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'CM - Scale heat and cool density maps'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 8 # CM_ID is defined by the enegy research center of Martigny (CREM)
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80

#TODO ********************setup this URL depending on which version you are running***************************

CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER

#TODO ********************setup this URL depending on which version you are running***************************

TRANFER_PROTOCOLE ='http://'

# Find available scenario data
import glob
import os
SD = "api_v1"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD
print(path)
fl = glob.glob("%s/my_calculation_module_directory/input_data/*RESULTS_ENERGY_*.csv" % path)
fl.sort()
print(len(fl))
available_scenarios = {}
available_years = []
for ele in fl:
    ele = ele.replace("\\","/").replace("//","/")
    ele = (ele.split("/")[-1]).split("_RESULTS_ENERGY_")
    scen = ele[0]
    yr = ele[1][:-4]
    print(scen)
    if scen not in available_scenarios.keys():
        available_scenarios[scen] = []
    available_scenarios[scen].append(str(yr))
    available_years.append(str(yr))

scenario_list= list(available_scenarios.keys())
year_list = list(set(available_years))
INPUTS_CALCULATION_MODULE = [

    {'input_name': 'Select scenario',
     'input_type': 'select',
     'input_parameter_name': 'scenario',
     'input_value': scenario_list,
     'input_unit': 'none',
     'input_min': 'none',
     'input_max': 'none', 'cm_id': CM_ID
     },
    {'input_name': 'Select target year',
     'input_type': 'select',
     'input_parameter_name': 'target_year',
     'input_value': year_list,
     'input_unit': 'none',
     'input_min': 'none',
     'input_max': 'none', 'cm_id': CM_ID
     },
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period before 1977',
     'input_type': 'input',
     'input_parameter_name': 'red_area_77',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period 1977-1990',
     'input_type': 'input',
     'input_parameter_name': 'red_area_80',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     }, 
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period after 1990',
     'input_type': 'input',
     'input_parameter_name': 'red_area_00',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period before 1977',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_77',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period 1977-1990',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_80',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period after 1990',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_00',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 50,
     'input_max': 200,
     'cm_id': CM_ID
     }
]


SIGNATURE = {

    "category": "Buildings",
    "authorized_scale":["NUTS 3", "NUTS 2", "NUTS 1","NUTS 0"],
    "cm_name": CM_NAME,
    "layers_needed": [
        "country_id_number",
        "nuts_id_number",
        "lau2_id_number",
        "gfa_res_curr_density_tif",
        "gfa_nonres_curr_density_tif",
        "heat_res_curr_density_tif",
        "heat_nonres_curr_density_tif",
        "ghs_built_1975_100_share",
        "ghs_built_1990_100_share",
        "ghs_built_2000_100_share",
        "ghs_built_2014_100_share",
    ],
    "type_layer_needed": [
        "heat",
    ],
    "vectors_needed": [
        "heating_technologies_eu28",

    ],
    "cm_url": "Do not add something",
    "cm_description": "this computation module calcuates the impact of renovation and building demolishment on future hdm ",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
