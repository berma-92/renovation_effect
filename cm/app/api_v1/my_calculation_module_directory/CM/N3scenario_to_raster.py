# -*- coding: utf-8 -*-
'''
This script has been created in the context of the Hotmaps EU project.

@author: Andreas Mueller
@Institute: TUW, Austria
@Contact: mueller@eeg.tuwien.ac.at
'''

import numpy as np
import time
import os, sys
import pyximport
pyximport.install()

from CM.helper_functions.exportLayerDict import export_layer as expLyr
import CM.helper_functions.cyf.create_density_map as CDM
from CM.helper_functions.read_raster import raster_array as RA
"""
import CM.helper_functions.cliprasterlayer as CRL


def getData(fn, geotransform_obj, size, data_type):
    
    
    ARR, geotransform_obj = CRL.clip_raster_layer(fn
                , geotransform_obj
                , size
                , data_type=data_type) 
        
    return ARR
"""

def CalcEffectsAtRasterLevel(NUTS_RESULTS_GFA_BASE
                            , NUTS_RESULTS_GFA_FUTURE
                            , NUTS_RESULTS_ENERGY_BASE
                            , NUTS_RESULTS_ENERGY_FUTURE
                            , NUTS_RESULTS_ENERGY_FUTURE_abs
                            , COUNTRY_id
                            , NUTS_id
                            , LAU2_id
                            , cp_share_1975
                            , cp_share_1990
                            , cp_share_2014
                            , fn_BUILDING_FOOTPRINT
                            , fn_ENERGY_RES
                            , fn_ENERGY_NRES
                            , fn_GFA_RES
                            , fn_GFA_NRES
                            , geotransform_obj, size
                            , csv_data_table
                            , output_raster_files
                            , output_csv_result
                            , add_inputs_parameters
                            , debug_output=False):

    RESULTS = {}
    RESULTS["Done"] = False
    try:
        COUNTRY_id.shape
    except:
        COUNTRY_id = np.ones_like(NUTS_id) * COUNTRY_id
        
    data_type = "f4"
    #debug_output = True
    adoption_bgf = add_inputs_parameters["adoption_bgf"]
    adoption_sp_ene = add_inputs_parameters["adoption_sp_ene"]
    base_year = add_inputs_parameters["base_year"]
    target_year = add_inputs_parameters["target_year"]

    output_raster_energy_tot = output_raster_files["output_raster_energy_tot"] 
    output_raster_gfa_tot = output_raster_files["output_raster_gfa_tot"] 
    if debug_output == True:
        pass
        '''
        output_raster_energy_res = output_raster_files["output_raster_energy_res"]
        output_raster_energy_nres = output_raster_files["output_raster_energy_nres"]
        output_raster_energy_res_rel = output_raster_files["output_raster_energy_res_rel"] 
        output_raster_energy_nres_rel = output_raster_files["output_raster_energy_nres_rel"] 
        output_raster_energy_tot_rel = output_raster_files["output_raster_energy_tot_rel"] 
        
        
        output_raster_gfa_res = output_raster_files["output_raster_gfa_res"]
        output_raster_gfa_nres = output_raster_files["output_raster_gfa_nres"]
        output_raster_gfa_res_rel = output_raster_files["output_raster_gfa_res_rel"] 
        output_raster_gfa_nres_rel = output_raster_files["output_raster_gfa_nres_rel"] 
        output_raster_gfa_tot_rel = output_raster_files["output_raster_gfa_tot_rel"] 
        '''
    
    #return RESULTS
    
    output_path = os.path.dirname(os.path.abspath(output_raster_energy_tot))
    if os.path.exists(output_path) == False:
        os.mkdir(output_path)

    if debug_output == True:
        pass
        '''
        csv_results = np.zeros((np.max(LAU2_id)+1, 165), dtype="f4")
        header = {}
        oNUTS = 26
        oCOUNTRY = 26
        '''
    energy_tot_future_existB = np.zeros((cp_share_1975.shape), dtype=data_type)
    energy_tot_curr = np.zeros_like(energy_tot_future_existB)
    gfa_tot_future_existB = np.zeros_like(energy_tot_future_existB)
    gfa_tot_curr_initial_year = np.zeros_like(energy_tot_future_existB)
    
    
    _gfa_cur__ = 0
    _gfa_fut__ = 0
    _ene_cur__ = 0
    _ene_fut__ = 0
    
    AREA_PER_CP = np.zeros((2,4), dtype="f4") 
    ENERGY_PER_CP = np.zeros((2,4), dtype="f4")
    #return RESULTS
    for i in range(2):
        energy_current = np.zeros_like(energy_tot_future_existB)
        energy_future = np.zeros_like(energy_tot_future_existB)
        
        area_future = np.zeros_like(energy_tot_future_existB)
        area_current = np.zeros_like(energy_tot_future_existB)
    
        CP_area_initial_nuts = np.zeros((NUTS_RESULTS_GFA_BASE.shape[0]+1, 4), dtype="f4")
        CP_area_future_nuts = np.zeros((NUTS_RESULTS_GFA_FUTURE.shape[0]+1, 4), dtype="f4")
        Share_cp_energy_initial = np.zeros((NUTS_RESULTS_ENERGY_BASE.shape[0]+1, 3), dtype="f4")
        Share_cp_energy_future = np.zeros((NUTS_RESULTS_ENERGY_FUTURE.shape[0]+1, 3), dtype="f4")
    
        if i == 0:
            print("Calc RES")
            
            # ENERGY_RES
            ENERGY = RA(fn_ENERGY_RES, dType=data_type)
            # GFA_RES 
            BGF_intial = RA(fn_GFA_RES, dType=data_type)
            print("initial BGF and Energy Res")
            print(np.sum(BGF_intial / 10**6))
            print(np.sum(ENERGY / 10**6))
            CP_area_initial_nuts[1:, 0] = (NUTS_RESULTS_GFA_BASE["gfa_sfh_1977"] + NUTS_RESULTS_GFA_BASE["gfa_mfh_1977"])
            CP_area_initial_nuts[1:, 1] = (NUTS_RESULTS_GFA_BASE["gfa_sfh_77_90"] + NUTS_RESULTS_GFA_BASE["gfa_mfh_77_90"])
            CP_area_initial_nuts[1:, 2] = (NUTS_RESULTS_GFA_BASE["gfa_sfh_90_17"] + NUTS_RESULTS_GFA_BASE["gfa_mfh_90_17"])
            CP_area_initial_nuts[1:, 3] = (NUTS_RESULTS_GFA_BASE["gfa_sfh_2017__"] + NUTS_RESULTS_GFA_BASE["gfa_mfh_2017__"])
            
            CP_area_future_nuts[1:, 0] = (NUTS_RESULTS_GFA_FUTURE["gfa_sfh_1977"] + NUTS_RESULTS_GFA_FUTURE["gfa_mfh_1977"])
            CP_area_future_nuts[1:, 1] = (NUTS_RESULTS_GFA_FUTURE["gfa_sfh_77_90"] + NUTS_RESULTS_GFA_FUTURE["gfa_mfh_77_90"])
            CP_area_future_nuts[1:, 2] = (NUTS_RESULTS_GFA_FUTURE["gfa_sfh_90_17"] + NUTS_RESULTS_GFA_FUTURE["gfa_mfh_90_17"])
            CP_area_future_nuts[1:, 3] = (NUTS_RESULTS_GFA_FUTURE["gfa_sfh_2017__"] + NUTS_RESULTS_GFA_FUTURE["gfa_mfh_2017__"])
            
            Share_cp_energy_initial[1:, 0] = 0.5 * (NUTS_RESULTS_ENERGY_BASE["share_sfh_1977"] + NUTS_RESULTS_ENERGY_BASE["share_mfh_1977"])
            Share_cp_energy_initial[1:, 1] = 0.5 * (NUTS_RESULTS_ENERGY_BASE["share_sfh_77_90"] + NUTS_RESULTS_ENERGY_BASE["share_mfh_77_90"])
            Share_cp_energy_initial[1:, 2] = 0.5 * (NUTS_RESULTS_ENERGY_BASE["share_sfh_90_17"] + NUTS_RESULTS_ENERGY_BASE["share_mfh_90_17"])
            
            Share_cp_energy_future[1:, 0] = 0.5 * (NUTS_RESULTS_ENERGY_FUTURE["share_sfh_1977"] + NUTS_RESULTS_ENERGY_FUTURE["share_mfh_1977"])
            Share_cp_energy_future[1:, 1] = 0.5 * (NUTS_RESULTS_ENERGY_FUTURE["share_sfh_77_90"] + NUTS_RESULTS_ENERGY_FUTURE["share_mfh_77_90"])
            Share_cp_energy_future[1:, 2] = 0.5 * (NUTS_RESULTS_ENERGY_FUTURE["share_sfh_90_17"] + NUTS_RESULTS_ENERGY_FUTURE["share_mfh_90_17"])
            
 
            if debug_output == True:
                pass
                '''
                o = 0
                bt_type = "Res"
                fn_out_fp = output_raster_energy_res 
                fn_out_fp_rel = output_raster_energy_res_rel
                fn_out_fp_gfa = output_raster_gfa_res 
                fn_out_fp_rel_gfa = output_raster_gfa_res_rel
                '''

        else:
            print("Calc nRES")
            
            # GFA_NRES
            BGF_intial = RA(fn_GFA_NRES, dType=data_type)
            # ENERGY_NRES
            ENERGY = RA(fn_ENERGY_NRES, dType=data_type)
            print("initial BGF and Energy NonRes")
            print(np.sum(BGF_intial / 10**6))
            print(np.sum(ENERGY / 10**6))
            
            CP_area_initial_nuts = np.zeros((NUTS_RESULTS_GFA_BASE.shape[0]+1, 4), dtype="f4")
            CP_area_initial_nuts[1:, 0] = NUTS_RESULTS_GFA_BASE["gfa_nres_1977"]
            CP_area_initial_nuts[1:, 1] = NUTS_RESULTS_GFA_BASE["gfa_nres_77_90"]
            CP_area_initial_nuts[1:, 2] = NUTS_RESULTS_GFA_BASE["gfa_nres_90_17"]
            CP_area_initial_nuts[1:, 3] = NUTS_RESULTS_GFA_BASE["gfa_nres_2017__"]
            

            
            CP_area_future_nuts[1:, 0] = NUTS_RESULTS_GFA_FUTURE["gfa_nres_1977"]
            CP_area_future_nuts[1:, 1] = NUTS_RESULTS_GFA_FUTURE["gfa_nres_77_90"]
            CP_area_future_nuts[1:, 2] = NUTS_RESULTS_GFA_FUTURE["gfa_nres_90_17"]
            CP_area_future_nuts[1:, 3] = NUTS_RESULTS_GFA_FUTURE["gfa_nres_2017__"]
            
            
            Share_cp_energy_initial[1:, 0] = NUTS_RESULTS_ENERGY_BASE["share_nres_1977"]
            Share_cp_energy_initial[1:, 1] = NUTS_RESULTS_ENERGY_BASE["share_nres_77_90"]
            Share_cp_energy_initial[1:, 2] = NUTS_RESULTS_ENERGY_BASE["share_nres_90_17"]
            
            
            Share_cp_energy_future[1:, 0] = NUTS_RESULTS_ENERGY_FUTURE["share_nres_1977"]
            Share_cp_energy_future[1:, 1] = NUTS_RESULTS_ENERGY_FUTURE["share_nres_77_90"]
            Share_cp_energy_future[1:, 2] = NUTS_RESULTS_ENERGY_FUTURE["share_nres_90_17"]
            
            if debug_output == True:
                pass
                '''
                o = 80
                bt_type = "NRes"
                fn_out_fp = output_raster_energy_nres
                fn_out_fp_rel = output_raster_energy_nres_rel
                fn_out_fp_gfa = output_raster_gfa_nres 
                fn_out_fp_rel_gfa = output_raster_gfa_nres_rel
                '''
        
        # Future shares based on current area
        CP_area_future_nuts /= (np.ones((4,1),dtype="f4") 
                                 * np.maximum(0.1, np.sum(CP_area_initial_nuts, axis=1))).T
                                 
        CP_area_initial_nuts /= (np.ones((4,1),dtype="f4") 
                                 * np.maximum(0.1, np.sum(CP_area_initial_nuts, axis=1))).T
                                    
        
        
        """ """                  
        if debug_output == True:
            pass
            '''
            oL = o 
            oN = o + oNUTS
            oC = oN + oCOUNTRY
            TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(BGF_intial, LAU2_id) 
            TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(BGF_intial, NUTS_id) 
            TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(BGF_intial, COUNTRY_id) 
            # Get NUTS ID per LAU Region: 2 different versions
            # 1st From images
            NUTS_ID = np.rint(CDM.CreateResultsTableperIndicator(NUTS_id, LAU2_id, return_mean=1)).astype("uint32")[:,[0,3]]
            # 2nd via Table
            D = np.zeros((np.max(csv_data_table[0]["LAU_UNIQUEDATA_ID"])+1, 2), dtype="uint32")
            idx = csv_data_table[0]["LAU_UNIQUEDATA_ID"]
            D[idx, 1] = csv_data_table[0]["NUTS3_ID"]
            D[idx, 0] = idx
            
            NUTS3_ID = D[np.rint(TABLE_RESULTS_LAU[:,0]).astype("uint32"), 1]
            NUTS3_ID[NUTS3_ID > TABLE_RESULTS_NUTS[-1,0]] = 0
            header[0] = "LAU UNIQUEData ID"
            header[1] = "NUTS ID"
            header[2] = "NUTS ID"
            csv_results[:,:2] = NUTS_ID
            csv_results[:,2] = NUTS3_ID
            del D, idx
            C = np.zeros((np.max(csv_data_table[0]["LAU_UNIQUEDATA_ID"])+1,2), dtype="uint32")
            idx = csv_data_table[0]["LAU_UNIQUEDATA_ID"]
            C[idx, 1] = csv_data_table[0]["COUNTRY_ID"]
            C[idx, 0] = idx
            COUNTRY_ID = C[np.rint(TABLE_RESULTS_LAU[:,0]).astype("uint32"), 1]
            COUNTRY_ID[COUNTRY_ID > TABLE_RESULTS_COUNTRY[-1,0]] = 0
            
            header[3] = "COUNTRY_ID"
            csv_results[:,3] = COUNTRY_ID[:]
            
            """ 
            Initial BGF
            """ 
            col = 4 
            header[col + oL] = "Initial BGF total %s" % bt_type
            csv_results[:,col + oL] = TABLE_RESULTS_LAU[:,1]
            header[col + oN] = "Initial BGF total %s NUTS" % bt_type
            csv_results[:,col + oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1]
            header[col + oC] = "Initial BGF total %s Country" % bt_type
            csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            
            """ 
            Future BGF
            """ 
            
            col = 4 
            header[col + oL] = "Initial BGF total %s" % bt_type
            csv_results[:,col + oL] = TABLE_RESULTS_LAU[:,1]
            header[col + oN] = "Initial BGF total %s NUTS" % bt_type
            csv_results[:,col + oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1]
            header[col + oC] = "Initial BGF total %s Country" % bt_type
            csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            #'''        
        
        # CLuster construction periods: Until 1977; 1978 - 1990; 1991 - 2011
        # Run through construction periods
        for i_cp_ in range(3):
            print("Calc constr. period {}".format(i_cp_+1))
            if i_cp_ == 0:
                cp_share = cp_share_1975
            elif i_cp_ == 1:
                if i == 1:
                    del cp_share_1975
                cp_share = cp_share_1990
            else:
                if i == 1:
                    del cp_share_1990
                cp_share = cp_share_2014
                
            AREA = cp_share * BGF_intial
            TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(AREA, LAU2_id) 
            area_current += AREA
            AREA_PER_CP[0, i_cp_] += np.sum(TABLE_RESULTS_LAU[:,1])
            if debug_output == True:
                pass
                """
                TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(AREA, NUTS_id) 
                TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(AREA, COUNTRY_id) 
                col = 5+i_cp_
                header[col+oL] = "Initial BGF LAU %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]   
                header[col+oN] = "Initial BGF NUTS %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1] 
                header[col + oC] = "Initial BGF Country %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
                #"""

            SHARE_NUTS3_area_intial = CP_area_initial_nuts[:, i_cp_][NUTS_id]
            ratio_px_vs_NUTS = cp_share / (0.0001 + SHARE_NUTS3_area_intial)
                
            #ratio_px_vs_NUTS[:,:] = 1
            del SHARE_NUTS3_area_intial
            
            
            # RES FUTURE AREA
            AREA = AREA.copy()
            #Change of area per CP compared to initial year in precalculated scenario
            f_bgf = (CP_area_future_nuts[:, i_cp_] / np.maximum(0.00001, CP_area_initial_nuts[:, i_cp_]))[NUTS_id]
            
            adopt_factor_bgf = f_bgf * (1 - np.minimum(np.maximum(0, adoption_bgf[i_cp_]/100 * (1-f_bgf)), 1)) / np.maximum(0.0001, f_bgf)
            AREA *= adopt_factor_bgf
            
            # Now it is the future demand
            TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(AREA, LAU2_id) 
            area_future += AREA
            AREA_PER_CP[1, i_cp_] += np.sum(TABLE_RESULTS_LAU[:,1])
            if debug_output == True:
                pass
                """
                TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(AREA, NUTS_id) 
                TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(AREA, COUNTRY_id) 
    
                col = 9+i_cp_
                header[col+oL] = "Future BGF LAU %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]   
                header[col+oN] = "Future BGF NUTS %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1]
                header[col + oC] = "Future BGF Country %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
                #"""
            del AREA
            
            # CURRENT DEMAND
            
            SHARE_NUTS3_energy = ENERGY.copy()
            SHARE_NUTS3_energy *= ratio_px_vs_NUTS
            f_ene_cur = Share_cp_energy_initial[:, i_cp_][NUTS_id]
            SHARE_NUTS3_energy *= f_ene_cur
            
            # At this stage it is the current demand
            TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, LAU2_id) 
            energy_current += SHARE_NUTS3_energy
            ENERGY_PER_CP[0, i_cp_] += np.sum(TABLE_RESULTS_LAU[:,1])
           
            if debug_output == True:
                pass
                """
                TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, NUTS_id) 
                TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, COUNTRY_id) 
                col = 13+i_cp_
                header[col+oL] = "Current Demand LAU %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]   
                header[col+oN] = "Current Demand NUTS %s CP idx %i" % (bt_type, i_cp_ + 1) 
                csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1]
                header[col + oC] = "Current Demand Country %s CP idx %i" % (bt_type, i_cp_ + 1) 
                csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
                #"""
            #del SHARE_NUTS3_energy
            # RES FUTURE DEMAND
            #SHARE_NUTS3_energy = ENERGY.copy()
            #SHARE_NUTS3_energy *= ratio_px_vs_NUTS 
            #SHARE_NUTS3_energy *= f_ene_cur
            
            #Now calculate future demand
            #Integrate adoption factor bgf
            SHARE_NUTS3_energy *= adopt_factor_bgf
            del adopt_factor_bgf
            
            f_ene_fut = Share_cp_energy_future[:, i_cp_][NUTS_id]            
            spec_savings = np.round(1 - (f_ene_fut / np.maximum(0.0001, f_ene_cur * f_bgf)),3)
            del f_ene_fut, f_ene_cur, f_bgf
            
            adopt_factor_sp_ene = 1 - np.minimum(np.maximum(0, adoption_sp_ene[i_cp_]/100 * spec_savings), 1)
            del spec_savings
            
            #Integrate adopt_factor_sp_ene
            # Now it becomes the future demand
            SHARE_NUTS3_energy *= adopt_factor_sp_ene 
            del adopt_factor_sp_ene
            
            
            TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, LAU2_id) 
            energy_future += SHARE_NUTS3_energy
            ENERGY_PER_CP[1, i_cp_] += np.sum(TABLE_RESULTS_LAU[:,1])
            if debug_output == True:
                pass
                """
                TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, NUTS_id) 
                TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(SHARE_NUTS3_energy, COUNTRY_id) 
                col = 21+i_cp_
                header[col+oL] = "Future Demand LAU %s CP idx %i" % (bt_type, i_cp_ + 1)
                csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]   
                header[col+oN] = "Future Demand NUTS %s CP idx %i" % (bt_type, i_cp_ + 1) 
                csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID, 1]
                header[col + oC] = "Future Demand Country %s CP idx %i" % (bt_type, i_cp_ + 1) 
                csv_results[:,col + oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
                #"""
            del SHARE_NUTS3_energy
            
            
            
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(energy_future, LAU2_id)
        _ene_fut__ += np.sum(TABLE_RESULTS_LAU[:,1])
        if debug_output == True:
            pass
            """
            
            TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(energy_future, NUTS_id)
            TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(energy_future, COUNTRY_id) 
            col = 25 
            header[col+oL] = "Future Demand LAU %s" % bt_type
            csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]
            header[col+oN] = "Future Demand NUTS %s"% bt_type
            csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
            header[col+oC] = "Future Demand Country %s"% bt_type
            csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            #"""
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(energy_current, LAU2_id)
        _ene_cur__ += np.sum(TABLE_RESULTS_LAU[:,1])
        if debug_output == True:
            pass
            """
            TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(energy_current, NUTS_id)
            TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(energy_current, COUNTRY_id) 
            col = 26 
            header[col+oL] = "CURRENT Demand LAU %s" % bt_type
            csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]
            header[col+oN] = "CURRENT Demand NUTS %s"% bt_type
            csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
            header[col+oC] = "CURRENT Demand Country %s"% bt_type
            csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            #"""
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(area_future, LAU2_id)
        _gfa_fut__ += np.sum(TABLE_RESULTS_LAU[:,1])
        if debug_output == True:
            pass
            """
            TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(area_future, NUTS_id)
            TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(area_future, COUNTRY_id)
            col = 27 
            header[col+oL] = "Future AREA LAU %s" % bt_type
            csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]
            header[col+oN] = "Future AREA NUTS %s"% bt_type
            csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
            header[col+oC] = "Future AREA Country %s"% bt_type
            csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            
            #"""
        
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(area_current, LAU2_id)
        _gfa_cur__ += np.sum(TABLE_RESULTS_LAU[:,1])
        if debug_output == True:
            pass
            """
            TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(area_current, NUTS_id)
            TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(area_current, COUNTRY_id)
            col = 28 
            header[col+oL] = "CURRENT AREA LAU %s" % bt_type
            csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]
            header[col+oN] = "CURRENT AREA NUTS %s"% bt_type
            csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
            header[col+oC] = "CURRENT AREA Country %s"% bt_type
            csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID, 1]
            
            #"""
        energy_tot_future_existB += energy_future
        energy_tot_curr += ENERGY
        
        if (area_future > BGF_intial).any():
            print("CHECK AREA FUTURE")
        gfa_tot_future_existB += area_future
        gfa_tot_curr_initial_year += BGF_intial
            
        if debug_output == True:
            pass
            """
            #Export IMAGE
            SaveLayerDict = {}
            
            if debug_output == True:
                SaveLayerDict["AA"] =   (fn_out_fp, geotransform_obj
                                                , "f4", energy_future  , 0)
                SaveLayerDict["AB"] =   (fn_out_fp_rel, geotransform_obj
                                                    , "f4", energy_future / np.maximum(0.00001, energy_current) , 0)
                
                SaveLayerDict["AC"] =   (fn_out_fp_gfa, geotransform_obj
                                                    , "f4", area_future  , 0)
                SaveLayerDict["AD"] =   (fn_out_fp_rel_gfa, geotransform_obj
                                                    , "f4", area_future / np.maximum(0.00001, BGF_intial) , 0)
                SaveLayerDict = expLyr(SaveLayerDict)
            
            
            
            if debug_output == True:
                SaveLayerDict["AA"] =   (output_raster_energy_tot, geotransform_obj
                                                    , "f4", energy_tot_future_existB  , 0)
                SaveLayerDict["AB"] =   (output_raster_energy_tot_rel, geotransform_obj
                                                    , "f4", energy_tot_future_existB / np.maximum(0.00001, energy_current) , 0)
                SaveLayerDict["AC"] =   (output_raster_gfa_tot, geotransform_obj
                                                    , "f4", gfa_tot_future_existB  , 0)
                SaveLayerDict["AD"] =   (output_raster_gfa_tot_rel, geotransform_obj
                                                    , "f4", gfa_tot_future_existB / np.maximum(0.00001, gfa_tot_curr_initial_year) , 0)
                SaveLayerDict = expLyr(SaveLayerDict)
            """
    del area_future, energy_future, energy_current, area_current, cp_share, cp_share_2014
    if debug_output == True:        
        pass
        """
        #INITIAL DEMAND JUST TO CHECK DATA
        
        TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(ENERGY, LAU2_id)
        TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(ENERGY, NUTS_id)
        TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(ENERGY, COUNTRY_id)
        col += 1 
        header[col+oL] = "INITIAL Demand LAU RES"
        csv_results[:,col+oL] = TABLE_RESULTS_LAU[:,1]
        #col += 1
        header[col+oN] = "INITIAL Demand NUTS RES"
        csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
        header[col+oC] = "INITIAL Demand Country RES"
        csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID,1]
        
        fn_out_csv = "%s" % output_csv_result
        notempty = csv_results[:, 1] > 0.1                   
        header_ = ""
        for k in range(csv_results.shape[1]):
            if k in header.keys():
                header_ += header[k] 
            header_ += ","
        try:
            np.savetxt(fn_out_csv, csv_results[notempty, :], delimiter = ",", header = header_, comments="")
        except:
            pass
        
        print("Done")
        #"""
    del ENERGY
    
    demand_new_build = (NUTS_RESULTS_ENERGY_FUTURE_abs['ene_sfh_2017__']
                           + NUTS_RESULTS_ENERGY_FUTURE_abs['ene_mfh_2017__']
                           + NUTS_RESULTS_ENERGY_FUTURE_abs['ene_nres_2017__'] + 0.001)
    
    area_new_buildings = (NUTS_RESULTS_GFA_FUTURE['gfa_sfh_2017__']
                           + NUTS_RESULTS_GFA_FUTURE['gfa_mfh_2017__']
                           + NUTS_RESULTS_GFA_FUTURE['gfa_nres_2017__'] + 0.00001)
 
    area_total_buildings_target = NUTS_RESULTS_GFA_FUTURE['gfa_total'] + 0.00001 
    area_existing_buildings_initial_yr = (NUTS_RESULTS_GFA_FUTURE['gfa_total_2017'] + 0.00001)
    
    """
        BGF New buildings
    """
    
    
    AREA_NEW_BUILD_per_existing_area = area_total_buildings_target / (0.000001+area_existing_buildings_initial_yr) # Total area in target year / total area in intial year
    AREA_NEW = np.maximum(0, gfa_tot_curr_initial_year * (AREA_NEW_BUILD_per_existing_area[np.maximum(1,NUTS_id) - 1]) - gfa_tot_future_existB)
    
    
    TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(AREA_NEW, LAU2_id)
    if debug_output == True:
        pass
        """
        TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(AREA_NEW, NUTS_id)
        TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(AREA_NEW, COUNTRY_id)
        col += 1 
        header[col+oL] = "BGF LAU NewBuild"
        csv_results[:TABLE_RESULTS_LAU.shape[0],col+oL] = TABLE_RESULTS_LAU[:,1]
        #col += 1
        header[col+oN] = "BGF NUTS NewBuild"
        csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
        header[col+oC] = "BGF Country NewBuild"
        csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID,1]
        #"""
    AREA_PER_CP[1,3] = np.sum(TABLE_RESULTS_LAU[:,1])
    
    """
        Energy New buildings
    """
    DEMAND_NEW_BUILD_per_area = (demand_new_build / area_new_buildings)
    DEMAND_NEW = AREA_NEW * DEMAND_NEW_BUILD_per_area[np.maximum(1,NUTS_id) - 1] / 1000
    TABLE_RESULTS_LAU = CDM.CreateResultsTableperIndicator(DEMAND_NEW, LAU2_id)
    if debug_output == True:
        pass
        
        TABLE_RESULTS_NUTS = CDM.CreateResultsTableperIndicator(DEMAND_NEW, NUTS_id)
        TABLE_RESULTS_COUNTRY = CDM.CreateResultsTableperIndicator(DEMAND_NEW, COUNTRY_id)
        col += 1 
        header[col+oL] = "Future Demand LAU NEW_build"
        csv_results[:TABLE_RESULTS_LAU.shape[0],col+oL] = TABLE_RESULTS_LAU[:,1]
        #col += 1
        header[col+oN] = "Future Demand NUTS NEW_build"
        csv_results[:,col+oN] = TABLE_RESULTS_NUTS[NUTS3_ID,1]
        header[col+oC] = "Future Demand Country NewBuild"
        csv_results[:,col+oC] = TABLE_RESULTS_COUNTRY[COUNTRY_ID,1]
        #"""
    
    ENERGY_PER_CP[1,3] = np.sum(TABLE_RESULTS_LAU[:,1]) 
    #return RESULTS
    ########################
    #
    # Calculate distribution of new buildings
    #
    ########################
    new_construction_methode = add_inputs_parameters["new_constructions"].lower().strip()
    print(np.sum(gfa_tot_future_existB)/1000)
    print(np.sum(energy_tot_future_existB)/1000)
    #return RESULTS
    if new_construction_methode.startswith("no"):
        future_gfa_map = gfa_tot_future_existB
        future_ene_map = energy_tot_future_existB
        share_of_new_constructions_shown_in_map = 0
    elif new_construction_methode.startswith("replace") or new_construction_methode.startswith("add"):
        future_gfa_map = np.minimum(gfa_tot_future_existB + AREA_NEW, gfa_tot_curr_initial_year) # future gfa if new area only replaces existing one
        share_new_build =  np.maximum(0, future_gfa_map - gfa_tot_future_existB) / np.maximum(0.0001, AREA_NEW) # calculate for each cell: share of distributed new area vs total new AREA
        print(np.max(share_new_build))
        print(np.min(share_new_build))
        future_ene_map = energy_tot_future_existB + share_new_build * DEMAND_NEW 
        share_of_new_constructions_shown_in_map = np.maximum(0, np.sum(future_gfa_map - gfa_tot_future_existB) / np.maximum(0.0001, np.sum(AREA_NEW))) 
        print(np.sum(future_gfa_map))
        if new_construction_methode.startswith("add"):
            
            
            max_add_floor_by_increase_floors = 0.15 * gfa_tot_curr_initial_year
            """if (target_year - base_year) <= 20:
                size_ = 3
            else:
                size_ = 5
            """
            #print(1)
            #calculated_average_of_neigbhors = ndimage.generic_filter(BUILDING_FOOTPRINT, np.nanmean, size=size_, mode='constant', cval=np.NaN)
            if os.path.exists(fn_BUILDING_FOOTPRINT):
                try:
                    
                    BUILDING_FOOTPRINT = RA(fn_BUILDING_FOOTPRINT, dType=data_type)
                except:
                    BUILDING_FOOTPRINT = (gfa_tot_curr_initial_year) / 4.
            else:
                BUILDING_FOOTPRINT = (gfa_tot_curr_initial_year) / 4.
            
            calculated_average_of_neigbhors = np.zeros_like(BUILDING_FOOTPRINT)
            calculated_average_of_neigbhors[:,:] += BUILDING_FOOTPRINT
            for row in range(-1,2):
                for col in range(-1,2):
                    calculated_average_of_neigbhors[2:-2,2:-2] += BUILDING_FOOTPRINT[2+row:-2+row,2+col:-2+col]
            calculated_average_of_neigbhors = np.maximum(calculated_average_of_neigbhors / 9, BUILDING_FOOTPRINT)
            #print(2)
            max_add_floor_new_areas = (gfa_tot_curr_initial_year / np.maximum(0.00001, BUILDING_FOOTPRINT) * 
                                        np.minimum(calculated_average_of_neigbhors * ((target_year - base_year)/80), np.maximum(0.6 - BUILDING_FOOTPRINT / 10000,0)))
            upper_limit_additional_area = max_add_floor_by_increase_floors + max_add_floor_new_areas
            
            missing_new_build_area = (1 - share_of_new_constructions_shown_in_map) * np.sum(AREA_NEW)
            
            exloitation_rate_of_limit = np.sum(missing_new_build_area) / np.sum(upper_limit_additional_area)
            
            add_new_gfa = exloitation_rate_of_limit * upper_limit_additional_area
            future_gfa_map += add_new_gfa
            
            ene_new_buildings = (future_gfa_map - gfa_tot_future_existB) * DEMAND_NEW_BUILD_per_area[np.maximum(1,NUTS_id) - 1] / 1000
            ene_new_buildings *= np.minimum(1.5, np.maximum(0.6, ENERGY_PER_CP[1,3] /  
                                                        np.maximum(0.00000000001, np.sum(ene_new_buildings))))
            future_ene_map = energy_tot_future_existB + ene_new_buildings
            
            share_of_new_constructions_shown_in_map = np.minimum(1.01, np.sum(future_gfa_map - gfa_tot_future_existB) / np.maximum(0.0001, np.sum(AREA_NEW)))
        
    else:
        future_gfa_map = gfa_tot_future_existB
        future_ene_map = energy_tot_future_existB
        share_of_new_constructions_shown_in_map = 0
    print("Future bgf and energy total")
    print(np.sum(future_gfa_map)/10**6)
    print(np.sum(future_ene_map)/10**6)
    
    
    #return RESULTS
    SaveLayerDict = {}
    SaveLayerDict["AA"] =   (output_raster_energy_tot, geotransform_obj
                                            , "f4", future_ene_map  , 0)
    SaveLayerDict["AC"] =   (output_raster_gfa_tot, geotransform_obj
                                        , "f4", future_gfa_map  , 0)
    SaveLayerDict = expLyr(SaveLayerDict)
    #return RESULTS
            

    _gfa_fut__ += AREA_PER_CP[1,3]
    _ene_fut__ += ENERGY_PER_CP[1,3]
    
    RESULTS["gfa_cur"] = _gfa_cur__
    
    RESULTS["gfa_cur"] = _gfa_cur__
    RESULTS["gfa_fut"] = _gfa_fut__
    RESULTS["ene_cur"] = _ene_cur__
    RESULTS["ene_fut"] = _ene_fut__
    RESULTS["spe_ene_cur"] = _ene_cur__ / _gfa_cur__ * 1000
    RESULTS["spe_ene_fut"] = _ene_fut__ / _gfa_fut__ * 1000
    RESULTS["share_of_new_constructions_shown_in_map"] = share_of_new_constructions_shown_in_map * 100
    
    
    RESULTS["gfa_75_fut"] = AREA_PER_CP[1,0]
    RESULTS["gfa_80_fut"] = AREA_PER_CP[1,1]
    RESULTS["gfa_00_fut"] = AREA_PER_CP[1,2]
    RESULTS["gfa_new_fut"] = AREA_PER_CP[1,3]
    
    RESULTS["ene_75_fut"] = ENERGY_PER_CP[1,0]
    RESULTS["ene_80_fut"] = ENERGY_PER_CP[1,1]
    RESULTS["ene_00_fut"] = ENERGY_PER_CP[1,2]
    RESULTS["ene_new_fut"] = ENERGY_PER_CP[1,3]
    
    RESULTS["gfa_75_cur"] = AREA_PER_CP[0,0]
    RESULTS["gfa_80_cur"] = AREA_PER_CP[0,1]
    RESULTS["gfa_00_cur"] = AREA_PER_CP[0,2]
    RESULTS["gfa_new_cur"] = AREA_PER_CP[0,3]
    
    RESULTS["ene_75_cur"] = ENERGY_PER_CP[0,0]
    RESULTS["ene_80_cur"] = ENERGY_PER_CP[0,1]
    RESULTS["ene_00_cur"] = ENERGY_PER_CP[0,2]
    RESULTS["ene_new_cur"] = ENERGY_PER_CP[0,3]
    
    RESULTS["spec_ene_75_fut"] = RESULTS["ene_75_fut"] / RESULTS["gfa_75_fut"] * 1000
    RESULTS["spec_ene_80_fut"] = RESULTS["ene_80_fut"] / RESULTS["gfa_80_fut"] * 1000
    RESULTS["spec_ene_00_fut"] = RESULTS["ene_00_fut"] / RESULTS["gfa_00_fut"] * 1000
    RESULTS["spec_ene_new_fut"] = RESULTS["ene_new_fut"] / np.maximum(0.00001, RESULTS["gfa_new_fut"])  * 1000
    
    RESULTS["spec_ene_75_cur"] = RESULTS["ene_75_cur"] / RESULTS["gfa_75_cur"] * 1000
    RESULTS["spec_ene_80_cur"] = RESULTS["ene_80_cur"] / RESULTS["gfa_80_cur"] * 1000
    RESULTS["spec_ene_00_cur"] = RESULTS["ene_00_cur"] / RESULTS["gfa_00_cur"] * 1000
    
    RESULTS["Done"] = True
    return RESULTS
    
            
            
