
CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'CM - Demand projection'
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
from time import gmtime, strftime
print("\n\n" +"*"*50 +"\n\n" + strftime("%Y-%m-%d %H:%M:%S", gmtime()))

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
    try:
        yr = int(yr)
        if yr > 2015:
            #print(scen)
            if scen not in available_scenarios.keys():
                available_scenarios[scen] = []
            available_scenarios[scen].append(str(yr))
            available_years.append(str(yr))
    except:
        pass


scenario_list= list(available_scenarios.keys())
year_list = sorted(list(set(available_years)))
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
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period before 1975',
     'input_type': 'input',
     'input_parameter_name': 'red_area_77',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period 1975-1990',
     'input_type': 'input',
     'input_parameter_name': 'red_area_80',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     }, 
    {'input_name': 'Reduction of floor area compared to reference scenario: Constr. period after 1990',
     'input_type': 'input',
     'input_parameter_name': 'red_area_00',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period before 1975',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_77',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period 1975-1990',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_80',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Reduction of specific energy needs compared to reference scenario: Constr. period after 1990',
     'input_type': 'input',
     'input_parameter_name': 'red_sp_ene_00',
     'input_value': 100,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 200,
     'cm_id': CM_ID
     },
    {'input_name': 'Annual population growth in addition to default growth',
     'input_type': 'input',
     'input_parameter_name': 'add_population_growth',
     'input_value': 0,
     'input_unit': '%p.a.',
     'input_min': -3,
     'input_max': +3,
     'cm_id': CM_ID
     },
    {'input_name': 'Method to add newly constructed buildings to map',
     'input_type': 'select',
     'input_parameter_name': 'new_constructions',
     'input_value': ["No new buildings","Replace only demolished buildings","Add all new buildings"],
     'input_unit': 'none',
     'input_min': 'none',
     'input_max': 'none', 'cm_id': CM_ID
     }
]


SIGNATURE = {

    "category": "Demand",
    "authorized_scale":["NUTS 3", "NUTS 2", "NUTS 1","LAU 2", "Hectare"],
    "cm_name": CM_NAME,
    "description_link": "https://github.com/HotMaps/hotmaps_wiki/wiki/en-CM-Demand-projection",
    "layers_needed": [],
    "type_layer_needed": [
         {"type" : "country_id_number","description" : "Country ID according to Hotmaps dataset."},
        {"type" : "nuts_id_number","description" : "NUTS3 ID according to Hotmaps dataset."},
        {"type" : "lau2_id_number","description" : "LAU ID according to Hotmaps dataset."},
        {"type" : "gfa_res_curr_density","description" : "Be aware to the use residential heated floor area layer."},
        {"type" : "gfa_nonres_curr_density","description" : "Be aware to use the NON-residential heated floor area layer."},
        {"type" : "heat_res_curr_density","description" : "Be aware to use the residential heat density layer."},
        {"type" : "heat_nonres_curr_density","description" : "Be aware to use NON-residential heat density layer."},
        {"type" : "ghs_built_1975_100_share","description" : "Layer with share of building constructed until 1975 in base year."},
        {"type" : "ghs_built_1990_100_share","description" : "Layer with share of building constructed from 1976-1989 in base year."},
        {"type" : "ghs_built_2000_100_share","description" : "Layer with share of building constructed from 1990-1999 in base year."},
        {"type" : "ghs_built_2014_100_share","description" : "Layer with share of building constructed from 2000-2014 in base year."},
        {"type" : "building_footprint_tot_curr","description" : "Be aware to use the building footprint layer of buildings."},
        {"type" : "pop_tot_curr_density","description" : "Be aware to use the population layer of 2011."}
    ],
    "cm_url": "Do not add something",
    "cm_description": "this computation module calcuates the impact of renovation and building demolishment on future hdm ",
    "cm_id": CM_ID,
    "wiki_url":"https://wiki.hotmaps.eu/en/CM-Demand-projection",
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
