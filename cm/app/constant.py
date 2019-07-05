
CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'calculation_module_test'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 1 # CM_ID is defined by the enegy research center of Martigny (CREM)
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80

#TODO ********************setup this URL depending on which version you are running***************************

CELERY_BROKER_URL = CELERY_BROKER_URL_LOCAL
PORT = PORT_LOCAL

#TODO ********************setup this URL depending on which version you are running***************************

TRANFER_PROTOCOLE ='http://'

INPUTS_CALCULATION_MODULE = [

    {'input_name': 'Select scenario',
     'input_type': 'select',
     'input_parameter_name': 'scenario',
     'input_value': ["Scenario 1",
                   "Scenario 2"],
     'input_unit': 'none',
     'input_min': 'none',
     'input_max': 'none', 'cm_id': CM_ID
     },
    {'input_name': 'Select target year',
     'input_type': 'select',
     'input_parameter_name': 'target_year',
     'input_value': ["2030",
                   "2040",
                   "2050"],
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
        "nuts_id",
        "gfa_res",
        "energy_res",
        "lau2_id",
        "cp_share_1975",
        "cp_share_1990",
        "cp_share_2000",
        "cp_share_2014",
    ],
    "type_layer_needed": [
        "heat",
    ],

    "cm_url": "Do not add something",
    "cm_description": "this computation module calcuates the impact of renovation and building demolishment on future hdm ",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
