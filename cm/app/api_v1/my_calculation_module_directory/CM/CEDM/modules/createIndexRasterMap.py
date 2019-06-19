'''
Created on Feb 2, 2018

@author: simulant
'''

import time, ogr
import os, sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

import  CEDM.modules.query as qu 
import  CEDM.modules.rasterize as ra  
    
def createIndexMap(in_vector_path
              , out_vectpr_path
              , extent
              , geotransform_Object
              , arr_size
              , noDataValue
              , dataType
              , key_field = "NUTS_ID"
              , value_field = "IDNUMBER"
              , out_field_name = "IDNUMBER"):
    
    # Create Raster Map which contains the ID Number of the Region to which the pixel belongs
    print("_createIndexMap")


    st1 = time.time()
    qu.query(in_vector_path, extent, in_vector_path, key_field
             , value_field, out_field_name, out_vectpr_path
             , outLayer_type = ogr.wkbPolygon)
    print ("Query took: %5.1f sec" % (time.time() - st1))

    st1 = time.time()
    #NUTS_REGION_Indicator contains the information about NUTS3 region on the level of hectar
    
    inVectorPath = out_vectpr_path
    (ARR_NUTS_REGION_Indicator, geotransform_obj) = ra.rasterize_no_centroid(inVectorPath
                        , value_field, dataType
                        , geotransform_Object
                        , arr_size
                        , noDataValue)
    

    print ("Rasterize took: %5.1f sec" % (time.time() - st1))

    
    return  ARR_NUTS_REGION_Indicator, geotransform_obj