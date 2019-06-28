import time

import os, sys
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD

if path not in sys.path:
    sys.path.append(path)
from CM.N3scenario_to_raster import CalcEffectsAtRasterLevel
from CM.helper_functions.readCsvData import READ_CSV_DATA
import CM.helper_functions.Subfunctions as SF
import CM.helper_functions.cliprasterlayer as CRL
from CM.helper_functions.exportLayerDict import export_layer as expLyr
from CM.helper_functions.read_raster import raster_array as RA


print(sys.version_info)




def main(input_raster_NUTS_id,
         input_raster_GFA_RES,
         input_raster_ENERGY_RES,
         input_raster_LAU2_id,
         input_raster_cp_share_1975,
         input_raster_cp_share_1990,
         input_raster_cp_share_2000,
         input_raster_cp_share_2014,
         output_raster_energy_res,
         output_raster_energy_nres,
         output_csv_result):
    
    st = time.time()
    #end_year = 2030
    #start_year = 2012
    data_type = "f4"
    data_type_int = "uint32"
    local_input_dir = path + "/input_data"
    
    NUTS_id, gt = RA(input_raster_NUTS_id, dType=data_type_int, return_gt=True)
    GFA_RES = RA(input_raster_GFA_RES, dType=data_type)
    ENERGY_RES = RA(input_raster_ENERGY_RES, dType=data_type)
    LAU2_id = RA(input_raster_LAU2_id, dType=data_type_int)
    cp_share_1975 = RA(input_raster_cp_share_1975, dType=data_type)
    cp_share_1990 = RA(input_raster_cp_share_1990, dType=data_type)
    cp_share_2000 = RA(input_raster_cp_share_2000, dType=data_type)
    cp_share_2014 = RA(input_raster_cp_share_2014, dType=data_type)
    
    NUTS_id_size = NUTS_id.shape
    cp_share_2000_and_2014 = cp_share_2000 + cp_share_2014

    
    NUTS_RESULTS_ENERGY_BASE = READ_CSV_DATA(local_input_dir + "/RESULTS_SHARES_2012.csv", skip_header=3)[0]
    NUTS_RESULTS_ENERGY_FUTURE = READ_CSV_DATA(local_input_dir + "/RESULTS_SHARES_2030.csv", skip_header=3)[0]
    NUTS_RESULTS_ENERGY_FUTURE_abs = READ_CSV_DATA(local_input_dir + "/RESULTS_ENERGY_2030.csv", skip_header=3)[0]
    NUTS_RESULTS_GFA_BASE = READ_CSV_DATA(local_input_dir + "/RESULTS_GFA_2012.csv", skip_header=3)[0]
    NUTS_RESULTS_GFA_FUTURE = READ_CSV_DATA(local_input_dir + "/RESULTS_GFA_2030.csv", skip_header=3)[0]
    csv_data_table = READ_CSV_DATA(local_input_dir + "/Communal2_data.csv", skip_header=6)
    
    
    #fn_res_bgf_initial = "%s/RESULTS_GFA_RES_BUILD.csv" % dirname
    
    _, _ = CalcEffectsAtRasterLevel(NUTS_RESULTS_GFA_BASE,
                                    NUTS_RESULTS_GFA_FUTURE,
                                    NUTS_RESULTS_ENERGY_BASE,
                                    NUTS_RESULTS_ENERGY_FUTURE,
                                    NUTS_RESULTS_ENERGY_FUTURE_abs,
                                    NUTS_id,
                                    LAU2_id,
                                    cp_share_1975,
                                    cp_share_1990,
                                    cp_share_2000_and_2014,
                                    ENERGY_RES,
                                    GFA_RES,
                                    gt,
                                    NUTS_id_size,
                                    csv_data_table,
                                    output_raster_energy_res,
                                    output_raster_energy_nres,
                                    output_csv_result)
    
    
    
    print("Done")
    
    
    

if __name__ == "__main__":
    print('calculation started')
    
    subdir = "cut/"
    dir_ = "../../../../tests/data"
    fn_reference_tif = "%s/%sREFERENCE.tif" % (dir_, subdir)
    fn_NUTS3_id_number = "%s/%sNUTS3_cut_id_number.tif" % (dir_, subdir)
    fn_gfa_res_curr = "%s/%sgfa_res_curr_density.tif" % (dir_, subdir)
    fn_heat_res_curr = "%s/%sheat_res_curr_density.tif" % (dir_, subdir)
    
    fn_LAU2_id_number = "%s/%sLAU2_id_number.tif" % (dir_, subdir)
    
    fn_GHS_BUILT_1975_100_share = "%s/%sGHS_BUILT_1975_100_share.tif" % (dir_, subdir)
    fn_GHS_BUILT_1990_100_share = "%s/%sGHS_BUILT_1990_100_share.tif" % (dir_, subdir)
    fn_GHS_BUILT_2000_100_share = "%s/%sGHS_BUILT_2000_100_share.tif" % (dir_, subdir)
    fn_GHS_BUILT_2014_100_share = "%s/%sGHS_BUILT_2014_100_share.tif" % (dir_, subdir)


    main(fn_reference_tif
         , fn_NUTS3_id_number
         , fn_gfa_res_curr
         , fn_heat_res_curr
         , fn_LAU2_id_number
         , fn_GHS_BUILT_1975_100_share
         , fn_GHS_BUILT_1990_100_share
         , fn_GHS_BUILT_2000_100_share
         , fn_GHS_BUILT_2014_100_share)

#import sys;sys.path.append(r'/home/simulant/.eclipse/org.eclipse.platform_3.8_155965261/plugins/org.python.pydev_4.5.5.201603221110/pysrc')
#import pydevd;pydevd.settrace()