import unittest
from werkzeug.exceptions import NotFound
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
UPLOAD_DIRECTORY = '/home/users/bmayr/workspace/projects_bernhard/datawarehouse/hotmaps/cm_files_uploaded/'


if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)


class TestAPI(unittest.TestCase):


    def setUp(self):
        self.app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app,)

    def tearDown(self):

        self.ctx.pop()


    def test_compute(self):
        
        
        test_dir = 'tests/data/'
        # raster file dir
        raster_file_dir = '%s/input/' % test_dir
        #raster_file_dir = 'tests/data'
        
        #raster_file_path0 = raster_file_dir + "/country_id_number.tif"
        raster_file_path1 = raster_file_dir + "/nuts3_id_number.tif"
        raster_file_path2 = raster_file_dir + "/gfa_res_curr_density.tif"
        raster_file_path3 = raster_file_dir + "/heat_res_curr_density.tif"
        raster_file_path2b = raster_file_dir + "/gfa_nonres_curr_density.tif"
        raster_file_path3b = raster_file_dir + "/heat_nonres_curr_density.tif"
        
        raster_file_path4 = raster_file_dir + "/lau2_id_number.tif"
        raster_file_path5 = raster_file_dir + "/ghs_built_1975_100_share.tif"
        raster_file_path6 = raster_file_dir + "/ghs_built_1990_100_share.tif"
        raster_file_path7 = raster_file_dir + "/ghs_built_2000_100_share.tif"
        raster_file_path8 = raster_file_dir + "/ghs_built_2014_100_share.tif"
        
        raster_file_path9 = raster_file_dir + "/building_footprint_tot_curr.tif"
        raster_file_path10 = raster_file_dir + "/pop_tot_curr_density.tif"

        # simulate copy from HTAPI to CM
        #save_path0 = UPLOAD_DIRECTORY+"/country_cut_id_number.tif"
        save_path1 = UPLOAD_DIRECTORY+"/nuts3_cut_id_number.tif"
        save_path2 = UPLOAD_DIRECTORY+"/gfa_res_curr_density.tif"
        save_path3 = UPLOAD_DIRECTORY+"/heat_res_curr_density.tif"
        
        save_path2b = UPLOAD_DIRECTORY+"/gfa_nonres_curr_density.tif"
        save_path3b = UPLOAD_DIRECTORY+"/heat_nonres_curr_density.tif"        
        
        save_path4 = UPLOAD_DIRECTORY+"/lau2_id_number.tif"
        save_path5 = UPLOAD_DIRECTORY+"/ghs_built_1975_100_share.tif"
        save_path6 = UPLOAD_DIRECTORY+"/ghs_built_1990_100_share.tif"
        save_path7 = UPLOAD_DIRECTORY+"/ghs_built_2000_100_share.tif"
        save_path8 = UPLOAD_DIRECTORY+"/ghs_built_2014_100_share.tif"
        save_path9 = UPLOAD_DIRECTORY+"/building_footprint_tot_curr.tif"
        save_path10 = UPLOAD_DIRECTORY+"/pop_tot_curr_density.tif"
        
        #copyfile(raster_file_path0, save_path0)
        copyfile(raster_file_path1, save_path1)
        copyfile(raster_file_path2, save_path2)
        copyfile(raster_file_path3, save_path3)
        copyfile(raster_file_path2b, save_path2b)
        copyfile(raster_file_path3b, save_path3b)
        
        copyfile(raster_file_path4, save_path4)
        copyfile(raster_file_path5, save_path5)
        copyfile(raster_file_path6, save_path6)
        copyfile(raster_file_path7, save_path7)
        copyfile(raster_file_path8, save_path8)
        copyfile(raster_file_path9, save_path9)
        copyfile(raster_file_path10, save_path10)


        inputs_raster_selection = {}
        inputs_parameter_selection = {}
        inputs_vector_selection = {}
        
        inputs_parameter_selection['scenario'] = "hotmaps_renovation_rate_1perc"
        inputs_parameter_selection['target_year'] = "2040"
        inputs_parameter_selection['red_area_77'] = "100"
        inputs_parameter_selection['red_area_80'] = "100"
        inputs_parameter_selection['red_area_00'] = "100"
        inputs_parameter_selection['red_sp_ene_77'] = "100"
        inputs_parameter_selection['red_sp_ene_80'] = "100"
        inputs_parameter_selection['red_sp_ene_00'] = "100"
        inputs_parameter_selection['add_population_growth'] = "0"
        inputs_parameter_selection['new_constructions'] = "No new buildings"
        
        #inputs_raster_selection["country_id_number"] = save_path0
        inputs_raster_selection["nuts_id_number"] = save_path1
        inputs_raster_selection["gfa_res_curr_density"] = save_path2
        inputs_raster_selection["heat_res_curr_density"] = save_path3
        inputs_raster_selection["gfa_nonres_curr_density"] = save_path2b
        inputs_raster_selection["heat_nonres_curr_density"] = save_path3b
        
        inputs_raster_selection["lau2_id_number"] = save_path4
        inputs_raster_selection["ghs_built_1975_100_share"] = save_path5
        inputs_raster_selection["ghs_built_1990_100_share"] = save_path6
        inputs_raster_selection["ghs_built_2000_100_share"] = save_path7
        inputs_raster_selection["ghs_built_2014_100_share"] = save_path8
        inputs_raster_selection["building_footprint_tot_curr"] = save_path9
        inputs_raster_selection["pop_tot_curr_density"] = save_path10
        

        # register the calculation module a
        payload = {"inputs_raster_selection": inputs_raster_selection,
                   "inputs_parameter_selection": inputs_parameter_selection,
                   #"inputs_vector_selection": inputs_vector_selection
                   }


        rv, json = self.client.post('computation-module/compute/', data=payload)

        self.assertTrue(rv.status_code == 200)


