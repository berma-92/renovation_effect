import gdal, ogr, os, osr, time
import numpy as np
import sys


import CM_intern.common_modules.array2raster as a2r
try:
    import CM_intern.CEDM.modules.cyf.SumOfHighRes as HRcFunction
    
except:
    print("SumOfHighRes in\nCM_intern.calc_energy_density.modules.cython_files"+
          "\nNeeds to compiled first")
    sys.exit()
'''

This code considers the input raster with a lower resolution (e.g.: 1km2) and outputs a raster with a higher resolution (e.g.100m2). 
In case, different configuration in term of resolution
is required, the corresponding ResIncreaseFactor  should b set

'''

def HighRes(inRasterPath
            , dataType, outRasterPath, noDataValue
            , ResIncreaseFactor=10
            , saveAsRaster= False):
    
    if int(ResIncreaseFactor) < ResIncreaseFactor:
        print("Resolution must be Integer Value")
        print("Exit Script")
        sys.exit
        
    inDatasource = gdal.Open(inRasterPath)
    geotransform_obj = inDatasource.GetGeoTransform()
    #minx = geotransform_obj[0]
    #maxy = geotransform_obj[3]

    b = inDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    
    arr_out, geotransform_obj = HighResArray(arr, ResIncreaseFactor, geotransform_obj)
    
    inDatasource = None

    if saveAsRaster == True:
        a2r.array2rasterfile(outRasterPath, geotransform_obj, dataType
                         , arr_out, noDataValue) # convert array to raster
        
    return (outRasterPath, geotransform_obj, dataType
                         , arr_out, noDataValue)
    
def HighResArray(arr_in, ResIncreaseFactor, geotransform_ob):
    """ 
    Transform just the array
    """
    geotransform_ob_new = (geotransform_ob[0], geotransform_ob[1] / ResIncreaseFactor, 0
                           , geotransform_ob[3], 0, geotransform_ob[5] / ResIncreaseFactor) 
    return (HRcFunction.CalcHighRes(arr_in, ResIncreaseFactor), geotransform_ob_new)

    
if __name__ == "__main__":
    start_time = time.time()
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    noDataValue = 0
    outRasterPath = prj_path+os.sep+"Pop_1km_100m.tif"
    pixelHeight=100
    pixelWidth=100
    inRasterPath= data_path + os.sep + "Population.tif"
    dataType = "float32"
    HighRes(inRasterPath, pixelWidth, pixelHeight, dataType, outRasterPath, noDataValue)
    elapsed_time = time.time() - start_time
    print(elapsed_time)