
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
'''
INPUTS_CALCULATION_MODULE = [
    
]
'''

SIGNATURE = {

    "category": "Buildings",
    "authorized_scale":["NUTS 3", "NUTS 2", "NUTS 1","NUTS 0","Hectare"],
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
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
#    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
